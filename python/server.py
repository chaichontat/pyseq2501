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


DEBUG = True
imager = FakeImager if DEBUG else Imager(get_ports(60))

def take_img(n_bundles: int, dark: bool = False) -> Callable[[], str]:
    def inner() -> str:
        img = imager.take(n_bundles, dark=dark)
        pil_img = Image.fromarray((img[1] / 8).astype(np.uint8))
        buff = BytesIO()
        pil_img.save(buff, format="JPEG")
        return base64.b64encode(buff.getvalue()).decode("utf-8")
    return inner


Cmds = Literal["take", "stop", "eject", "laser_r", "laser_g", "x", "y", "z_obj", "z_tilt", "init"]

class Received(BaseModel):
    __match_args__ = ("cmd", "n")
    cmd: Cmds
    n: Optional[int]
    

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
                        await websocket.send_text(imgstr)
                
            except WebSocketDisconnect:
                ...


app.websocket("/status")(status.gen_poll(imager))
# app.get("/logs")(status.logs)

    
# %%

