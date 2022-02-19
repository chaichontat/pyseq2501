import asyncio
import logging
import os
from concurrent.futures import Future
from dataclasses import dataclass
from typing import AsyncGenerator, Callable, Coroutine, NoReturn

from fastapi import Request, WebSocket, WebSocketDisconnect
from pydantic import BaseModel
from websockets.exceptions import ConnectionClosedOK

from pyseq2.imager import Imager, Position

logger = logging.getLogger(__name__)


class Moves(BaseModel):
    pos: float
    in_position: bool


class Status(State):
    x: int
    y: int
    z_tilt: tuple[int, int, int]
    z_obj: int
    laser_r: int
    laser_g: int
    shutter: bool
    moving: bool
    msg: str


def gen_poll(imager: Imager):
    async def poll(websocket: WebSocket) -> NoReturn:
        while True:
            try:
                await websocket.accept()
                while True:
                    if os.name == "nt":
                        pos, lasers = await asyncio.gather(
                            imager.pos, imager.lasers.power
                        )
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
                    logger.info(u)
                    await asyncio.sleep(1)
            except (WebSocketDisconnect, ConnectionClosedOK):
                ...

    return poll


# Just use Terminal®.
# async def logGenerator(request: Request):
#     i = 0
#     while True:
#         yield i
#         await asyncio.sleep(1)
#         i += 1
#     # for line in tail("-f", LOGFILE, _iter=True):
#     #     if await request.is_disconnected():
#     #         print("client disconnected!!!")
#     #         break
#     #     yield line
#     #     time.sleep(0.5)


# async def logs(request: Request):
#     event_generator = logGenerator(request)
#     return EventSourceResponse(event_generator)
