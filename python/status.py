import asyncio
from typing import AsyncGenerator, Callable, Coroutine, NoReturn

from fastapi import Request, WebSocket, WebSocketDisconnect
from pydantic import BaseModel
from pyseq2.imager import Imager
from sse_starlette.sse import EventSourceResponse


class Moves(BaseModel):
    pos: float
    in_position: bool


class Status(BaseModel):
    x: float
    y: float
    z_tilt: tuple[int, int, int]
    z_obj: int
    laser_r: int
    laser_g: int
    shutter: bool
    moving: bool
    msg: str


def gen_poll(imager: Imager):
    async def poll(websocket: WebSocket) -> NoReturn:
        x = 10000
        y = -180000
        while True:
            await websocket.accept()
            while True:
                try:
                    await websocket.send_json(
                        Status(
                            x=x,
                            y=y,
                            z_tilt=(1, 1, 1),
                            z_obj=1,
                            laser_r=int(x / 10000),
                            laser_g=1,
                            shutter=False,
                            moving=False,
                            msg="Imaging",
                        ).json()
                    )
                    await asyncio.sleep(1)
                    x += 500
                    y += 50000
                    if x > 50000:
                        x = 0
                    if y > 5000000:
                        y = 0
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
