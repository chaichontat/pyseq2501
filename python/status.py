import asyncio
from concurrent.futures import Future
from dataclasses import dataclass
from typing import AsyncGenerator, Callable, Coroutine, NoReturn

from fastapi import Request, WebSocket, WebSocketDisconnect
from pydantic import BaseModel
from pyseq2.imager import Imager
from pyseq2.utils.utils import not_none
from sse_starlette.sse import EventSourceResponse


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


@dataclass
class StatusFuture:
    x: Future[int]
    y: Future[int]
    z_tilt: Future[tuple[int, int, int]]
    z_obj: Future[int]
    laser_r: Future[int]
    laser_g: Future[int]
    shutter: bool
    moving: bool
    msg: str

    def to_status(self) -> Status:
        return Status(
            x=self.x.result(),
            y=self.y.result(),
            z_tilt=self.z_tilt.result(),
            z_obj=self.z_obj.result(),
            laser_r=self.laser_r.result(),
            laser_g=self.laser_g.result(),
            shutter=self.shutter,
            moving=self.moving,
            msg=self.msg,
        )


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
            await websocket.accept()
            while True:
                try:
                    await websocket.send_json(
                        StatusFuture(
                            x=imager.x.pos,
                            y=imager.y.pos,
                            z_tilt=imager.z_tilt.pos,
                            z_obj=imager.z_obj.pos,
                            laser_r=imager.lasers.r.power,
                            laser_g=imager.lasers.g.power,
                            shutter=False,
                            moving=False,
                            msg="Imaging",
                        )
                        .to_status()
                        .json()
                    )
                    await asyncio.sleep(1)
                except WebSocketDisconnect:
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
