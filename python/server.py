#%%
from __future__ import annotations

import asyncio
import logging
import os
from concurrent.futures import ThreadPoolExecutor
from typing import Annotated, Literal, NoReturn

import numpy as np
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import Response
from PIL import Image
from pydantic import BaseModel, Field, root_validator, validator
from rich.logging import RichHandler
from websockets.exceptions import ConnectionClosedOK

from cmd_uid import NExperiment
from imaging import update_img
from pyseq2.experiment import *
from pyseq2.fakes import FakeFlowCells, FakeImager
from pyseq2.imager import AbstractImager, Imager, State
from pyseq2.utils.ports import FAKE_PORTS, get_ports
from status import poll_status

logging.basicConfig(
    level="INFO",
    format="[yellow]%(name)-10s[/] %(message)s",
    datefmt="[%X]",
    handlers=[RichHandler(markup=True)],
)

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

latest = np.random.randint(0, 256, (4, 1024, 1024), dtype=np.uint8)
img = update_img(latest)
imager: Imager
fcs: FlowCells

q: asyncio.Queue[bool] = asyncio.Queue()


@app.on_event("startup")
async def startup_event():
    global imager, fcs, q
    if os.environ.get("FAKE_HISEQ", "0") != "1":
        imager = await Imager.ainit(ports := await get_ports(60))
        fcs = await FlowCells.ainit(ports)

    else:
        imager = await FakeImager.ainit(FAKE_PORTS)
        fcs = await FakeFlowCells.ainit(FAKE_PORTS)


dark = np.zeros((2, 2048, 2048), dtype=np.uint8)


@app.websocket("/cmd")
async def cmd_endpoint(websocket: WebSocket) -> NoReturn:
    global latest, img
    while True:
        try:
            await websocket.accept()
            while True:
                cmd = await websocket.receive_text()
                print(cmd)
                match cmd:
                    # TODO Need to block UI when moving.
                    case "move":
                        logger.info(f"")
                        await imager.move(x=0)
                    case "capture" | "preview" as c:
                        p = userSettings.image_params
                        p.save = True if c == "capture" else False
                        latest = await userSettings.image_params.run(fcs, p.fc, imager)
                        img = update_img(latest)
                        await websocket.send_text("ok")
                    case "autofocus":
                        logger.info(f"Autofocus")
                        await imager.autofocus()
                        await websocket.send_text("ok")
                    case _ as x:
                        logger.error(f"What is this command {x}?")

        except (WebSocketDisconnect):
            ...


class NTakeImage(TakeImage):
    fc: bool
    n: int

    @classmethod
    def default(cls) -> NTakeImage:
        ori = super().default()
        return NTakeImage(**ori.dict(), fc=False, n=1)


class UserSettings(BaseModel):
    """None happens when the user left the input empty."""

    block: Literal["", "moving", "ejecting", "capturing", "previewing"]
    max_uid: int
    mode: Literal["automatic", "manual", "editingA", "editingB"]
    exps: tuple[NExperiment, NExperiment]
    image_params: NTakeImage

    @classmethod
    def default(cls) -> UserSettings:
        return UserSettings(
            block="",
            max_uid=2,
            mode="automatic",
            exps=(NExperiment.default(0), NExperiment.default(1)),
            image_params=NTakeImage.default(),
        )


userSettings = UserSettings.default()


@app.websocket("/user")
async def user_endpoint(websocket: WebSocket) -> NoReturn:
    global userSettings
    while True:
        await websocket.accept()
        while True:
            try:
                await websocket.send_json(userSettings.json())
                while True:
                    ret = await websocket.receive_json()
                    userSettings = UserSettings.parse_obj(ret)
                    logger.info(userSettings)
            except (WebSocketDisconnect, ConnectionClosedOK):
                ...


@app.get("/img")
async def get_img():
    global latest, img
    # LATEST = np.random.randint(0, 4096, (4, 1024, 1024))
    # LATEST = np.random.randint(0, 4096) * np.ones((4, 1024, 1024))
    # IMG = update_img(LATEST)
    return Response(img.json())


@app.get("/download")
async def download():
    fc = userSettings.image_params.fc
    return Response(
        yaml.dump(userSettings.exps[fc].to_experiment().dict(), sort_keys=False),
        media_type="application/yaml",
    )


@app.websocket("/status")
async def poll(websocket: WebSocket) -> NoReturn:
    # async def status_ping():
    #     while True:
    #         await websocket.send_json((await gen_status()).json())
    #         await asyncio.sleep(5)

    # task = asyncio.create_task(status_ping())
    while True:
        await poll_status(websocket, imager, q)


# app.get("/logs")(status.logs)
