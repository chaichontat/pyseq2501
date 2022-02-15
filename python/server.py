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
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, PlainTextResponse, Response
from PIL import Image
from pydantic import BaseModel, Field, root_validator, validator
from rich.logging import RichHandler
from websockets.exceptions import ConnectionClosedOK

from fake_imager import FakeImager
from pyseq2.experiment import *
from pyseq2.imager import Imager, Position
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


class Hist(BaseModel):
    counts: list[int]
    bin_edges: list[float]


class Img(BaseModel):
    n: int
    img: list[str]
    hist: list[Hist]
    channels: tuple[bool, bool, bool, bool]


DEBUG = False
imager: Imager
q: asyncio.Queue[Img] = asyncio.Queue()

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


def process_img(img: np.ndarray) -> str:
    cmap = plt.cm.get_cmap()
    norm = plt.Normalize(vmin=img.min(), vmax=img.max())
    img = (cmap(norm(img)) * 256).astype(np.uint8)

    buff = BytesIO()
    pil_img = Image.fromarray(img).convert("RGB")
    pil_img.save(buff, format="JPEG")
    return "data:image/jpg;base64," + base64.b64encode(buff.getvalue()).decode("utf-8")


def gen_hist(img: np.ndarray) -> Hist:
    hist, bin_edges = np.histogram(img.flatten(), 40)
    return Hist(counts=list(hist), bin_edges=list(bin_edges))


LATEST = np.random.randint(0, 256, (4, 1024, 1024), dtype=np.uint8)
dark = np.zeros((2, 2048, 2048), dtype=np.uint8)


def update_img(arr: np.ndarray):
    img = [process_img(i) for i in arr]
    hist = [gen_hist(i) for i in arr]
    return Img(n=8, img=img, hist=hist, channels=(True, True, True, True))


IMG = update_img(LATEST)


@app.websocket("/cmd")
async def cmd_endpoint(websocket: WebSocket) -> NoReturn:
    global LATEST, IMG
    while True:
        try:
            await websocket.accept()
            while True:
                cmd = await websocket.receive_text()
                print(cmd)
                match cmd.split("_"):
                    # TODO Need to block UI when moving.
                    case ["x", n]:
                        logger.info(f"X Go: {n}")
                        await imager.x.move(int(n))
                    case ["y", n]:
                        logger.info(f"Y Go: {n}")
                        await imager.y.move(int(n))
                    case ["take"]:
                        LATEST = np.random.randint(0, 4096, (4, 1024, 1024))
                        IMG = update_img(LATEST)
                        await websocket.send_text("ready")
                    case ["autofocus"]:
                        logger.info(f"Autofocus")
                        # q.put_nowait(Img(n=16, img="", hist=hist(np.random.randint(0, 4096, 1000000))))
                    # case Received("autofocus", _):
                    #     logger.info(f"Autofocus")
                    #     target, img = await imager.autofocus(channel=1)
                    #     await imager.z_obj.move(target)

        except (WebSocketDisconnect):
            ...


class ReagentGroup(BaseModel):
    group: str


class NReagent(BaseModel):
    uid: str | int
    reagent: Reagent | ReagentGroup


class NCmd(BaseModel):
    uid: str | int
    cmd: Annotated[Pump | Prime | Temp | Hold | Autofocus | TakeImage | Move, Field(discriminator="op")]


class Recipe(BaseModel):
    name: str
    flowcell: Literal[0, 1]
    reagents: list[NReagent]
    cmds: list[NCmd]

    def to_experiment(self) -> Experiment:
        print(self.dict())
        return Experiment(
            name=self.name,
            flowcell=self.flowcell,
            reagents={r.reagent.name: r.reagent for r in self.reagents},
            cmds=[c.cmd for c in self.cmds],
        )


class ManualParams(BaseModel):
    n: int
    name: str
    path: str
    channels: tuple[bool, bool, bool, bool]


class UserSettings(BaseModel):
    """None happens when the user left the input empty."""

    x: float | None
    y: float | None
    z_tilt: int | None
    z_obj: int | None
    laser_r: int | None
    laser_g: int | None
    flowcell: bool
    max_uid: int
    mode: Literal["automatic", "manual", "editingA", "editingB"]
    recipes: tuple[Recipe | None, Recipe | None]
    man_params: ManualParams


recipe_default = Recipe(
    name="default",
    flowcell=0,
    reagents=[NReagent(uid=0, reagent=Reagent(name="water", port=1))],
    cmds=[NCmd(uid=0, cmd=Pump(reagent="water"))],
)


USERSETTINGS = UserSettings(
    x=0,
    y=0,
    z_tilt=19850,
    z_obj=32000,
    laser_r=5,
    laser_g=5,
    flowcell=False,
    max_uid=2,
    mode="automatic",
    recipes=(recipe_default.copy(), recipe_default.copy()),
    man_params=ManualParams(n=16, name="", path="", channels=(True, True, True, True)),
)


@app.websocket("/user")
async def user_endpoint(websocket: WebSocket) -> NoReturn:
    global USERSETTINGS
    while True:
        await websocket.accept()
        while True:
            try:
                await websocket.send_json(USERSETTINGS.json())
                while True:
                    ret = await websocket.receive_json()
                    USERSETTINGS = UserSettings.parse_obj(ret)
                    logger.info(USERSETTINGS)
            except (WebSocketDisconnect, ConnectionClosedOK):
                ...


@app.get("/img")
async def get_img():
    global LATEST, IMG
    # LATEST = np.random.randint(0, 4096, (4, 1024, 1024))
    # LATEST = np.random.randint(0, 4096) * np.ones((4, 1024, 1024))
    # IMG = update_img(LATEST)
    return Response(IMG.json())


@app.get("/download")
async def download():
    assert (r := USERSETTINGS.recipes[0]) is not None
    return Response(
        yaml.dump(recipe_default.to_experiment().dict(), sort_keys=False), media_type="application/yaml"
    )


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
                await asyncio.sleep(5)
        except (WebSocketDisconnect, ConnectionClosedOK):
            ...


# app.get("/logs")(status.logs)


# %%
