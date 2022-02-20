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


# class Status(State):
#     x: int
#     y: int
#     z_tilt: tuple[int, int, int]
#     z_obj: int
#     laser_r: int
#     laser_g: int
#     shutter: bool
#     moving: bool
#     msg: str


async def poll_status(websocket: WebSocket, imager: Imager, q: asyncio.Queue[bool]):
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
