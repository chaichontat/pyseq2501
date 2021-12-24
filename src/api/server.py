#%%
import asyncio
import base64
import logging
import sys
from concurrent.futures import ThreadPoolExecutor
from io import BytesIO
from pathlib import Path

import numpy as np
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from PIL import Image
from pydantic import BaseModel

sys.path.append((Path(__file__).parent.parent.parent).as_posix())
from rich.logging import RichHandler
from src.imager import Imager
from src.utils.ports import get_ports

logging.basicConfig(
    level="NOTSET",
    format="[yellow]%(name)-10s[/] %(message)s",
    datefmt="[%X]",
    handlers=[RichHandler(rich_tracebacks=True, markup=True)],
)

logging.getLogger("DCAMAPI").setLevel(logging.INFO)
logging.getLogger("matplotlib.font_manager").setLevel(logging.INFO)

app = FastAPI()
thr = ThreadPoolExecutor(max_workers=1)
# imager = Imager(get_ports(60))


class Status(BaseModel):
    x: float
    y: float
    z_tilt: tuple[int, int, int]
    z_obj: int
    laser_r: int
    laser_g: int
    shutter: bool


def take_img() -> str:
    imager.y.move(4000000)
    img = imager.take(8, dark=True)
    # print(i := np.random.randint(0, 256))
    pil_img = Image.fromarray((img[1] / 8).astype(np.uint8))
    buff = BytesIO()
    pil_img.save(buff, format="JPEG")
    return base64.b64encode(buff.getvalue()).decode("utf-8")


def fake() -> str:
    print(i := np.random.randint(0, 256))
    pil_img = Image.fromarray(i * np.ones((256, 256), dtype=np.uint8))
    buff = BytesIO()
    pil_img.save(buff, format="JPEG")
    return base64.b64encode(buff.getvalue()).decode("utf-8")


@app.websocket("/img")
async def websocket_endpoint(websocket: WebSocket):
    while True:
        await websocket.accept()
        while True:
            try:
                cmd = await websocket.receive_text()
                if cmd == "take":
                    imgstr = await asyncio.get_running_loop().run_in_executor(thr, take_img)
                    await websocket.send_text(imgstr)
            except WebSocketDisconnect:
                ...


@app.websocket("/status")
async def status(websocket: WebSocket):
    while True:
        await websocket.accept()
        x = 0
        y = 1
        while True:
            try:
                await websocket.send_json(
                    Status(x=x, y=y, z_tilt=(1, 1, 1), z_obj=1, laser_r=y, laser_g=1, shutter=False).json()
                )
                await asyncio.sleep(1)
            except WebSocketDisconnect:
                ...
            x += 0.3
            y += 1
            if x > 25:
                x = 0
            if y > 75:
                y = 0
