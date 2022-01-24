import asyncio
import logging
from concurrent.futures import Future
from dataclasses import dataclass
from typing import AsyncGenerator, Callable, Coroutine, NoReturn

from fastapi import Request, WebSocket, WebSocketDisconnect
from pydantic import BaseModel
from pyseq2.imager import Imager
from websockets.exceptions import ConnectionClosedOK

logger = logging.getLogger(__name__)


class Moves(BaseModel):
    pos: float
    in_position: bool


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


# @dataclass
# class :
#     x: Future[int]
#     y: Future[int]
#     z_tilt: Future[tuple[int, int, int]]
#     z_obj: int
#     laser_r: int
#     laser_g: int
#     shutter: bool
#     moving: bool
#     msg: str

    # def to_status(self) -> Status:
    #     return Status(
    #         x=self.x.result(),
    #         y=self.y.result(),
    #         z_tilt=self.z_tilt.result(),
    #         z_obj=self.z_obj.result(),
    #         laser_r=self.laser_r.result(),
    #         laser_g=self.laser_g.result(),
    #         shutter=self.shutter,
    #         moving=self.moving,
    #         msg=self.msg,
    #     )


# def gen_poll(imager: Imager):
#     async def poll(websocket: WebSocket) -> NoReturn:
#         x = 10000
#         y = -180000
#         while True:
#             await websocket.accept()
#             while True:
#                 try:
#                     await websocket.send_json(
#                         Status(
#                             x=x,
#                             y=y,
#                             z_tilt=(1, 1, 1),
#                             z_obj=1,
#                             laser_r=int(x / 10000),
#                             laser_g=1,
#                             shutter=False,
#                             moving=False,
#                             msg="Imaging",
#                         ).json()
#                     )
#                     await asyncio.sleep(1)
#                 except WebSocketDisconnect:
#                     ...
#     return poll


def gen_poll(imager: Imager):
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
