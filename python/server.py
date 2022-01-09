#%%
import asyncio
import base64
import logging
from concurrent.futures import ThreadPoolExecutor
from io import BytesIO
from typing import Callable, Literal, NoReturn, Optional

import numpy as np
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from PIL import Image
from pydantic import BaseModel, validator
from pyseq2.imager import Imager
from pyseq2.utils.ports import get_ports
from rich.logging import RichHandler

import status
from fake_imager import FakeImager

logging.basicConfig(
    level="INFO",
    format="[yellow]%(name)-10s[/] %(message)s",
    datefmt="[%X]",
    handlers=[RichHandler(rich_tracebacks=True, markup=True)],
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


DEBUG = False
imager = Imager(get_ports(60))

class Img(BaseModel):
    n: int
    img: str
    
Cmds = Literal["take", "stop", "eject", "laser_r", "laser_g", "x", "y", "z_obj", "z_tilt", "init"]



class Received(BaseModel):
    __match_args__ = ("cmd", "n")
    cmd: Cmds
    n: Optional[int]


def take_img(n_bundles: int, dark: bool = False) -> Callable[[], str]:
    def inner() -> str:
        img = imager.take(n_bundles, dark=dark)
        pil_img = Image.fromarray((img[1] / 8).astype(np.uint8))
        buff = BytesIO()
        pil_img.save(buff, format="JPEG")
        return base64.b64encode(buff.getvalue()).decode("utf-8")

    return inner


@app.websocket("/img")
async def image_endpoint(websocket: WebSocket) -> NoReturn:
    while True:
        await websocket.accept()
        while True:
            try:
                cmd = Received.parse_raw(await websocket.receive_text())
                match cmd:
                    case Received("take", n):
                        logger.info(f"Received: Take {n} bundles.")
                        imgstr = await asyncio.get_running_loop().run_in_executor(thr, take_img(n))
                        await websocket.send_json(Img(n=n, img=imgstr).json())
                    case Received("x", n):
                        logger.info(f"X Go: {n}")
                        await asyncio.get_running_loop().run_in_executor(thr, imager.x.move(n))
                    case Received("y", n):
                        logger.info(f"Y Go: {n}")
                        await asyncio.get_running_loop().run_in_executor(thr, imager.y.move(n))
                        
            except WebSocketDisconnect:
                ...


class UserSettings(BaseModel):
    n: int
    x: float
    y: float
    z_tilt: int
    z_obj: int
    laser_r: int
    laser_g: int
    flowcell: bool


USERSETTINGS = UserSettings(n=8, x=0, y=0, z_tilt=19850, z_obj=32000, laser_r=5, laser_g=5, flowcell=False)


@app.websocket("/user")
async def user_endpoint(websocket: WebSocket) -> NoReturn:
    global USERSETTINGS
    while True:
        await websocket.accept()
        await websocket.send_json(USERSETTINGS.json())
        while True:
            try:
                USERSETTINGS = UserSettings.parse_raw(await websocket.receive_text())
                logger.info(USERSETTINGS)
            except WebSocketDisconnect:
                ...


app.websocket("/status")(status.gen_poll(imager))
# app.get("/logs")(status.logs)


# %%
