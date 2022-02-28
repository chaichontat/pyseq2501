from __future__ import annotations

import asyncio
import logging
from typing import Literal, NoReturn

from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from fastapi.encoders import jsonable_encoder
from pydantic import BaseModel
from websockets.exceptions import ConnectionClosedOK

from pyseq2.imager import Imager, State

logger = logging.getLogger(__name__)

router = APIRouter()
BlockState = Literal["", "moving", "capturing", "previewing"]
q_status: asyncio.Queue[bool]


class FCState(BaseModel):
    running: bool
    step: int
    msg: str

    @classmethod
    def default(cls) -> FCState:
        return FCState(step=0, running=False, msg="")


class WebState(State):
    fcs: tuple[FCState, FCState]
    block: BlockState
    msg: str


message = "Idle"
state = WebState(**State.default().dict(), fcs=(FCState.default(), FCState.default()), block="", msg=message)


def update_block(b: BlockState):
    state.block = b
    try:
        q_status.put_nowait(True)
    except AttributeError:
        ...


async def poll_state(ws: WebSocket) -> NoReturn:
    global q_status, state
    imager: Imager = ws.app.state.imager
    q_status = ws.app.state.q_status
    wait_time = 5
    while True:
        try:
            wait_time = 5 if await asyncio.wait_for(q_status.get(), wait_time) else 0.5
        except asyncio.TimeoutError:
            ...
        finally:
            try:
                state = WebState.parse_obj(state.dict() | (await imager.state).dict())
            except asyncio.CancelledError as e:
                raise e
            except BaseException as e:
                logger.error(f"Status error: {type(e).__name__}: {e}")
                wait_time = 5
                # state.msg = f"Status error: {type(e).__name__}: {e

        if wait_time != 5:
            await ws.send_json(jsonable_encoder(state))


@router.websocket("/status")
async def poll_msg(ws: WebSocket):
    """
    Get status every 5 seconds

    Args:
      websocket (WebSocket): The websocket connection to the client.
      imager (Imager): Imager
      q_log (asyncio.Queue[str]): asyncio.Queue[str]
    """
    global message
    q_log: asyncio.Queue[str] = ws.app.state.q_log

    task = asyncio.create_task(poll_state(ws))
    await ws.accept()
    await ws.send_json(jsonable_encoder(state))

    try:
        while True:
            message = await q_log.get()
            state.msg = message
            await ws.send_json(jsonable_encoder(state))
    except (WebSocketDisconnect, RuntimeError, ConnectionClosedOK):
        ...
    finally:
        task.cancel()
