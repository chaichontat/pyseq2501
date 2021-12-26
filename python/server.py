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

sys.path.append((Path(__file__).parent.parent.parent).as_posix())
from fastapi.middleware.cors import CORSMiddleware
from rich.logging import RichHandler
from src.imager import Imager
from src.utils.ports import get_ports

import status

logging.basicConfig(
    level="NOTSET",
    format="[yellow]%(name)-10s[/] %(message)s",
    datefmt="[%X]",
    handlers=[RichHandler(rich_tracebacks=True, markup=True)],
)

logging.getLogger("sse_starlette.sse").setLevel(logging.INFO)
logging.getLogger("DCAMAPI").setLevel(logging.INFO)
logging.getLogger("matplotlib.font_manager").setLevel(logging.INFO)

app = FastAPI()
thr = ThreadPoolExecutor(max_workers=1)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
# imager = Imager(get_ports(60))


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


app.get("/status")(status.poll)
# app.get("/logs")(status.logs)
