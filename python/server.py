#%%
import asyncio
import base64
import logging
from concurrent.futures import ThreadPoolExecutor
from io import BytesIO
from typing import Literal, NoReturn, Optional

import matplotlib
import matplotlib.pyplot as plt
import numpy as np
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from PIL import Image
from pydantic import BaseModel
from pyseq2.imager import Imager
from pyseq2.utils.ports import get_ports
from rich.logging import RichHandler
from websockets.exceptions import ConnectionClosedOK

matplotlib.use('Agg')
import status
from fake_imager import FakeImager

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


DEBUG = False
imager: Imager
q = asyncio.Queue()
latest = np.zeros((2,2048,2048),dtype=np.uint8)
dark = np.zeros((2,2048,2048),dtype=np.uint8)

class Img(BaseModel):
    n: int
    img: str
    
Cmds = Literal["take", "stop", "eject", "laser_r", "laser_g", "x", "y", "z_obj", "z_tilt", "init", "autofocus"]

@app.on_event("startup")
async def startup_event():
    global imager
    imager = await Imager.ainit(await get_ports(60))


class Received(BaseModel):
    __match_args__ = ("cmd", "n")
    cmd: str
    n: Optional[int]


@app.websocket("/cmd")
async def cmd_endpoint(websocket: WebSocket) -> NoReturn:
    while True:
        try:
            await websocket.accept()
            while True:
                cmd = Received.parse_raw(await websocket.receive_text())
                match cmd:
                    # TODO Need to block UI when moving.
                    case Received("x", n):
                        logger.info(f"X Go: {n}")
                        await imager.x.move(n)
                    case Received("y", n):
                        logger.info(f"Y Go: {n}")
                        await imager.y.move(n)
                    case Received("autofocus", _):
                        logger.info(f"Autofocus")
                        target, img = await imager.autofocus(channel=1)
                        await imager.z_obj.move(target)

        except (WebSocketDisconnect):
            ...
 
def process_img(img: np.ndarray) -> str:
    cmap = plt.cm.get_cmap()
    norm = plt.Normalize(vmin=img[1].min(), vmax=img[1].max())
    img = (cmap(norm(img[1])) * 256).astype(np.uint8)

    buff = BytesIO()
    pil_img = Image.fromarray(img).convert("RGB")
    pil_img.save(buff, format="JPEG")
    return "data:image/jpg;base64," + base64.b64encode(buff.getvalue()).decode("utf-8")



@app.websocket("/img")
async def image_endpoint(websocket: WebSocket) -> NoReturn:
    global latest, dark
    while True:
        try:
            await websocket.accept()
            while True:
                cmd = Received.parse_raw(await websocket.receive_text())
                match cmd:
                    case Received("take", n):
                        logger.info(f"Received: Take {n} bundles.")
                        latest = await imager.take(n, channels=frozenset((0,)))
                        await websocket.send_json(Img(n=n, img=process_img(latest)).json())
                
                    case Received("dark", n):
                        logger.info(f"Received: Take 16 dark bundles.")
                        dark = await imager.take(n, channels=frozenset((0,)), dark=True)
                        await websocket.send_json(Img(n=n, img=process_img(dark)).json())

                    case Received("corr", n):
                        await websocket.send_json(Img(n=n, img=process_img(np.clip(latest - dark, 0, 65535))).json())
                    
                    case Received("uncorr", n):
                        await websocket.send_json(Img(n=n, img=process_img(latest)).json())

                    case Received("autofocus", _):
                        logger.info(f"Autofocus")
                        target, inten = await imager.autofocus(channel=1)
                        fig, ax = plt.subplots()
                        ax.hist(inten, bins=50)
                        # fig.canvas.draw()
                        buf = BytesIO()
                        fig.savefig(buf, format="svg")
                        await websocket.send_json(Img(n=16, img=("data:image/png;base64," + base64.b64encode(buf.getvalue()).decode("utf-8"))).json())

        except (WebSocketDisconnect):
            ...

class UserSettings(BaseModel):
    """None happens when the user left the input empty."""
    n: int | None
    x: float | None
    y: float | None
    z_tilt: int | None
    z_obj: int | None
    laser_r: int | None
    laser_g: int | None
    flowcell: bool


USERSETTINGS = UserSettings(n=16, x=0, y=0, z_tilt=19850, z_obj=32000, laser_r=5, laser_g=5, flowcell=False)


@app.websocket("/user")
async def user_endpoint(websocket: WebSocket) -> NoReturn:
    global USERSETTINGS
    while True:
        try:
            await websocket.accept()
            await websocket.send_json(USERSETTINGS.json())
            while True:
                USERSETTINGS = UserSettings.parse_raw(await websocket.receive_text())
                logger.info(USERSETTINGS)
        except (WebSocketDisconnect, ConnectionClosedOK):
            ...


class Status(BaseModel):
    x: int
    y: int
    z_tilt: tuple[int, int, int]
    z_obj: int
    laser_r: int
    laser_g: int
    shutter: bool
    moving: bool
    msg: str

@app.websocket("/status")
async def poll(websocket: WebSocket) -> NoReturn:
    while True:
        try:
            await websocket.accept()
            while True:
                pos, lasers = await asyncio.gather(imager.pos, imager.lasers.power)

                await websocket.send_json(
                    u := Status(
                        x=pos.x,
                        y=pos.y,
                        z_tilt=pos.z_tilt,
                        z_obj=pos.z_obj,
                        laser_r=lasers[1],
                        laser_g=lasers[0],
                        shutter=False,
                        moving=False,
                        msg="Imaging",
                    )
                    .json()
                )
                logger.info(u)
                await asyncio.sleep(1)
        except (WebSocketDisconnect, ConnectionClosedOK):
                ...
# app.get("/logs")(status.logs)


# %%
