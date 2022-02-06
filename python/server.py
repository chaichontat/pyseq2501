#%%
import asyncio
import base64
import logging
import os
from asyncio import Queue
from concurrent.futures import ThreadPoolExecutor
from io import BytesIO
from typing import Annotated, Literal, NoReturn, Optional

import matplotlib
import matplotlib.pyplot as plt
import numpy as np
import seaborn as sns
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from PIL import Image
from pydantic import BaseModel, Field, root_validator, validator
from rich.logging import RichHandler
from websockets.exceptions import ConnectionClosedOK

from pyseq2.experiment import *
from pyseq2.imager import Imager, Position
from pyseq2.utils.ports import get_ports

sns.set()
matplotlib.use("Agg")
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
latest = np.zeros((2, 2048, 2048), dtype=np.uint8)
dark = np.zeros((2, 2048, 2048), dtype=np.uint8)


class Hist(BaseModel):
    counts: list[int]
    bin_edges: list[float]


class Img(BaseModel):
    n: int
    img: str
    hist: Hist


Cmds = Literal[
    "take",
    "stop",
    "eject",
    "laser_r",
    "laser_g",
    "x",
    "y",
    "z_obj",
    "z_tilt",
    "init",
    "autofocus",
]


@app.on_event("startup")
async def startup_event():
    global imager, q
    imager = None  # await Imager.ainit(await get_ports(60))


class Received(BaseModel):
    __match_args__ = ("cmd", "n")
    cmd: str
    n: Optional[int]


def process_img(img: np.ndarray) -> str:
    cmap = plt.cm.get_cmap()
    norm = plt.Normalize(vmin=img[1].min(), vmax=img[1].max())
    img = (cmap(norm(img[1])) * 256).astype(np.uint8)

    buff = BytesIO()
    pil_img = Image.fromarray(img).convert("RGB")
    pil_img.save(buff, format="JPEG")
    return "data:image/jpg;base64," + base64.b64encode(buff.getvalue()).decode("utf-8")


def hist(img: np.ndarray) -> Hist:
    hist, bin_edges = np.histogram(img.flatten(), 40)
    return Hist(counts=list(hist), bin_edges=list(bin_edges))

    # fig, ax = plt.subplots(figsize=(5,4), dpi=100)

    # sns.histplot(img.flatten(), ax=ax)
    # ax.set_xlabel("Intensity")
    # plt.tight_layout()
    # buf = BytesIO()
    # fig.savefig(buf, format="png")  # matplotlib does not support jpg.
    # out = "data:image/png;base64," + base64.b64encode(buf.getvalue()).decode("utf-8")
    # plt.close(fig)
    # return out


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
                        q.put_nowait(Img(n=16, img="", hist=hist(np.random.randint(0, 4096, 1000000))))
                    # case Received("autofocus", _):
                    #     logger.info(f"Autofocus")
                    #     target, img = await imager.autofocus(channel=1)
                    #     await imager.z_obj.move(target)

        except (WebSocketDisconnect):
            ...


@app.websocket("/img")
async def image_endpoint(websocket: WebSocket) -> NoReturn:
    global latest, dark
    while True:
        try:
            await websocket.accept()
            while True:
                img = await q.get()
                await websocket.send_json(img.json())
                q.task_done()

                # cmd = Received.parse_raw(await websocket.receive_text())
                # match cmd:
                #     case Received("take", n):
                #         logger.info(f"Received: Take {n} bundles.")
                #         latest = await imager.take(n, channels=frozenset((0,)))
                #         await websocket.send_json(Img(n=n, img=process_img(latest), hist=hist(latest)).json())

                #     case Received("dark", n):
                #         logger.info(f"Received: Take 16 dark bundles.")
                #         dark = await imager.take(n, channels=frozenset((0,)), dark=True)
                #         await websocket.send_json(Img(n=n, img=process_img(dark), hist=hist(latest)).json())

                #     case Received("corr", n):
                #         await websocket.send_json(
                #             Img(
                #                 n=n,
                #                 img=process_img(np.clip(latest - dark, 0, 65535)),
                #                 hist=hist(latest),
                #             ).json()
                #         )

                #     case Received("uncorr", n):
                #         await websocket.send_json(Img(n=n, img=process_img(latest), hist=hist(latest)).json())

                #     case Received("autofocus", _):
                #         logger.info(f"Autofocus")
                #         await websocket.send_json(
                #             Img(n=16, img="", hist=hist(np.random.randint(0, 4096, 1000000))).json()
                #         )

        except (WebSocketDisconnect):
            ...


class NReagent(BaseModel):
    uid: str | int
    reagent: Reagent | str


class NCmd(BaseModel):
    uid: str | int
    cmd: Annotated[Pump | Prime | Temp | Hold | Autofocus | Image | Move, Field(discriminator="op")]


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
    mode: Literal["automatic", "manual"]
    reagents: list[NReagent]
    cmds: list[NCmd]
    max_uid: int  # Counter


USERSETTINGS = UserSettings(
    n=16,
    x=0,
    y=0,
    z_tilt=19850,
    z_obj=32000,
    laser_r=5,
    laser_g=5,
    flowcell=False,
    mode="automatic",
    reagents=[NReagent(uid=0, reagent=Reagent(name="", port=1))],
    cmds=[NCmd(uid=0, cmd=Pump(reagent=""))],
    max_uid=2,
)


@app.websocket("/user")
async def user_endpoint(websocket: WebSocket) -> NoReturn:
    global USERSETTINGS
    while True:
        try:
            await websocket.accept()
            await websocket.send_json(USERSETTINGS.json())
            while True:
                ret = await websocket.receive_json()
                logger.info(ret)
                USERSETTINGS = UserSettings.parse_obj(ret)
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
                if os.name == "nt":
                    pos, lasers = await asyncio.gather(imager.pos, imager.lasers.power)
                else:
                    pos, lasers = Position(0, 0, (0, 0, 0), 0), (0, 0)

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
                    ).json()
                )
                # logger.info(u)
                await asyncio.sleep(1)
        except (WebSocketDisconnect, ConnectionClosedOK):
            ...


# app.get("/logs")(status.logs)


# %%
