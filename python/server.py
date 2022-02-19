#%%
from __future__ import annotations

import asyncio
import logging
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
from fake_imager import FakeImager
from imaging import update_img
from pyseq2.experiment import *
from pyseq2.imager import AbstractImager, Imager, State
from pyseq2.utils.ports import get_ports

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

debug = False
latest = np.random.randint(0, 256, (4, 1024, 1024), dtype=np.uint8)
img = update_img(latest)
imager: AbstractImager
q: asyncio.Queue[bool] = asyncio.Queue()


@app.on_event("startup")
async def startup_event():
    global imager, q
    imager = await Imager.ainit(await get_ports(60))


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
                    case "take":
                        latest = np.random.randint(0, 4096, (4, 1024, 1024))
                        img = update_img(latest)
                        await websocket.send_text("ready")
                    case "autofocus":
                        logger.info(f"Autofocus")
                    case _ as x:
                        logger.error(f"What is this command {x}?")

        except (WebSocketDisconnect):
            ...


class UserSettings(BaseModel):
    """None happens when the user left the input empty."""

    block: Literal["", "moving", "ejecting", "capturing", "previewing"]
    max_uid: int
    mode: Literal["automatic", "manual", "editingA", "editingB"]
    experiments: tuple[NExperiment, NExperiment]
    image_params: TakeImage

    @classmethod
    def default(cls) -> UserSettings:
        return UserSettings(
            block="",
            max_uid=2,
            mode="automatic",
            experiments=(NExperiment.default(0), NExperiment.default(1)),
            image_params=TakeImage.default(),
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
    fc = userSettings.image_params.flowcell
    return Response(
        yaml.dump(userSettings.experiments[fc].to_experiment().dict(), sort_keys=False),
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
        try:
            await websocket.accept()
            while True:
                try:
                    await asyncio.wait_for(q.get(), 5)
                except asyncio.TimeoutError:
                    ...
                finally:
                    await websocket.send_json((await imager.state).json())
        except (WebSocketDisconnect, ConnectionClosedOK):
            ...


# app.get("/logs")(status.logs)
