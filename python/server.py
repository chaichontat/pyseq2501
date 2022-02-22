#%%
from __future__ import annotations

import asyncio
import io
import logging
import os
import time
from concurrent.futures import ThreadPoolExecutor
from contextlib import contextmanager
from typing import IO, Coroutine, Generator, Literal, NoReturn

import numpy as np
from fastapi import FastAPI, HTTPException, UploadFile, WebSocket, WebSocketDisconnect
from fastapi.encoders import jsonable_encoder
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, StreamingResponse
from PIL import Image
from pydantic import BaseModel
from rich.logging import RichHandler
from websockets.exceptions import ConnectionClosedOK

from cmd_uid import NExperiment
from imaging import update_img
from pyseq2.experiment import *
from pyseq2.fakes import FakeFlowCells, FakeImager
from pyseq2.imager import Imager
from pyseq2.utils.ports import FAKE_PORTS, get_ports
from status import poll_status

logging.basicConfig(
    level="INFO",
    format="[yellow]%(name)-10s[/] %(message)s",
    datefmt="[%X]",
    handlers=[RichHandler(markup=True)],
)

# Disable uvicorn loggers.
logging.getLogger("uvicorn.access").handlers = []
for _log in ["uvicorn", "uvicorn.error", "fastapi"]:
    _logger = logging.getLogger(_log)
    _logger.handlers = []

logger = logging.getLogger(__name__)
app = FastAPI()
thr = ThreadPoolExecutor(max_workers=1)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

latest = np.random.randint(0, 256, (4, 128, 2048), dtype=np.uint8)
img = update_img(latest)
imager: Imager
fcs: FlowCells


class CommandResponse(BaseModel):
    step: tuple[int, int, int] | None = None
    msg: str | None = None
    error: str | None = None


q_cmd: asyncio.Queue[CommandResponse | tuple[int, int, int]] = asyncio.Queue()
q_user: asyncio.Queue[None] = asyncio.Queue()


@app.on_event("startup")
async def startup_event():
    global imager, fcs, q_cmd
    if os.environ.get("FAKE_HISEQ", "0") != "1":
        imager = await Imager.ainit(ports := await get_ports(60))
        fcs = await FlowCells.ainit(ports)

    else:
        imager = await FakeImager.ainit(FAKE_PORTS)
        fcs = await FakeFlowCells.ainit(FAKE_PORTS)


dark = np.zeros((2, 2048, 2048), dtype=np.uint8)


@contextmanager
def q_listener(f: Coroutine[None, None, None]) -> Generator[None, None, None]:
    task = asyncio.create_task(f)
    try:
        yield
    finally:
        task.cancel()


@app.websocket("/cmd")
async def cmd_endpoint(websocket: WebSocket) -> None:
    async def ret_cmd() -> NoReturn:
        while True:
            res = await q_cmd.get()
            print(res)
            if isinstance(res, CommandResponse):
                to_send = res
            else:
                to_send = CommandResponse(step=res)

            print(f"sending {to_send}")
            await websocket.send_json(jsonable_encoder(to_send))

    global latest, img
    await websocket.accept()
    with q_listener(ret_cmd()):
        try:
            while True:
                cmd = await websocket.receive_text()
                print(cmd)
                try:
                    match cmd:
                        # TODO Need to block UI when moving.
                        case "move":
                            logger.info(f"")
                            await imager.move(x=0)
                        case "capture" | "preview" as c:
                            logger.info(c)
                            p = userSettings.image_params.copy()
                            if c == "capture":
                                p.save = True
                                p.z_from, p.z_to = 0, 0
                            else:
                                p.save = False
                            latest = await userSettings.image_params.run(fcs, p.fc, imager, q_cmd)  # type: ignore
                            logger.info("Capture completed")
                            img = update_img(latest)
                            logger.info("Image updated")
                            await asyncio.sleep(0.1)

                            logger.info("ok_put")
                        case "autofocus":
                            logger.info(f"Autofocus")
                            await imager.autofocus()
                            q_cmd.put_nowait(CommandResponse(msg="ok"))
                        case "stop":
                            q_cmd.put_nowait(CommandResponse(msg="ok"))
                        case _ as x:
                            logger.error(f"What is this command {x}?")

                    q_cmd.put_nowait(CommandResponse(msg="ok"))  # Doesn't seem to send with 1.
                    q_cmd.put_nowait(CommandResponse(msg="ok"))

                except BaseException as e:
                    q_cmd.put_nowait(CommandResponse(error=f"Error: {type(e).__name__}: {e}"))
                    q_cmd.put_nowait(CommandResponse(error=f"Error: {type(e).__name__}: {e}"))

        except (WebSocketDisconnect, RuntimeError, ConnectionClosedOK):
            ...


class NTakeImage(TakeImage):
    fc: bool

    @classmethod
    def default(cls) -> NTakeImage:
        ori = super().default()
        return NTakeImage(**ori.dict(), fc=False)


class UserSettings(BaseModel):
    """None happens when the user left the input empty."""

    block: Literal["", "moving", "ejecting", "capturing", "previewing"]
    max_uid: int
    mode: Literal["automatic", "manual", "editingA", "editingB"]
    exps: list[NExperiment]
    image_params: NTakeImage

    @classmethod
    def default(cls) -> UserSettings:
        return UserSettings(
            block="",
            max_uid=2,
            mode="automatic",
            exps=[NExperiment.default(False), NExperiment.default(True)],
            image_params=NTakeImage.default(),
        )


userSettings = UserSettings.default()


@app.websocket("/user")
async def user_endpoint(websocket: WebSocket) -> None:
    async def ret_user() -> NoReturn:
        while True:
            await q_user.get()
            await websocket.send_json(jsonable_encoder(userSettings))

    global userSettings
    await websocket.accept()
    with q_listener(ret_user()):
        try:
            await websocket.send_json(jsonable_encoder(userSettings))
            while True:
                ret = await websocket.receive_json()
                userSettings = UserSettings.parse_obj(ret)
                logger.info(userSettings)
        except (WebSocketDisconnect, RuntimeError, ConnectionClosedOK):
            ...


@app.websocket("/status")
async def poll(websocket: WebSocket) -> None:
    # async def status_ping():
    #     while True:
    #         await websocket.send_json((await gen_status()).json())
    #         await asyncio.sleep(5)

    # task = asyncio.create_task(status_ping())
    await websocket.accept()
    try:
        while True:
            await poll_status(websocket, imager, q_cmd)
    except (WebSocketDisconnect, RuntimeError, ConnectionClosedOK):
        ...


@app.get("/img")
async def get_img():
    global latest, img
    # LATEST = np.random.randint(0, 4096, (4, 1024, 1024))
    # LATEST = np.random.randint(0, 4096) * np.ones((4, 1024, 1024))
    # IMG = update_img(LATEST)
    return JSONResponse(jsonable_encoder(img))


@app.get("/usersettings")
async def get_user():
    logger.info("Get usersettings.")
    return JSONResponse(jsonable_encoder(userSettings))


# @app.get("/experiment/{fc}")
# async def download(fc: int):
#     resp = StreamingResponse(
#         io.StringIO(yaml.safe_dump(userSettings.exps[fc].to_experiment().dict(), sort_keys=False)),
#         media_type="application/yaml",
#     )
#     print(userSettings.exps[fc].to_experiment())
#     resp.headers["Content-Disposition"] = f"attachment; filename={userSettings.exps[fc].name}.yaml"
#     return resp


# @app.post("/experiment/{fc}")
# async def create_file(fc: bool, file: UploadFile):
#     f: IO[bytes] = file.file  # type: ignore
#     try:
#         y = yaml.safe_load(f)
#         print(y)
#         ne = NExperiment.from_experiment(Experiment.parse_obj(y), userSettings.max_uid)
#         ne.fc = fc
#         userSettings.max_uid += len(ne.reagents) + len(ne.cmds)
#         userSettings.exps[fc] = ne

#         q_user.put_nowait(None)
#     except BaseException as e:
#         raise HTTPException(400, detail=f"{type(e).__name__}: {e}")
#     return "ok"
