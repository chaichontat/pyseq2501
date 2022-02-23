import asyncio
import logging
from typing import Literal, NoReturn

from fastapi import WebSocket
from fastapi.encoders import jsonable_encoder
from pydantic import BaseModel

from pyseq2.imager import Imager, State

logger = logging.getLogger(__name__)


class FCState(BaseModel):
    state: Literal["idle", "running"]
    step: int


class WebState(State):
    msg: str


message = "Idle"


async def poll_status(websocket: WebSocket, imager: Imager, q_log: asyncio.Queue[str]):
    global message
    while True:
        try:
            message = await asyncio.wait_for(q_log.get(), 5)
        except asyncio.TimeoutError:
            ...
        finally:
            state = WebState(**(await imager.state).dict(), msg=message)
            await websocket.send_json(jsonable_encoder(state))
