from __future__ import annotations

import asyncio
import logging
import time
from typing import Literal, NoReturn

from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from fastapi.encoders import jsonable_encoder
from pydantic import BaseModel
from websockets.exceptions import ConnectionClosedOK

from pyseq2.imager import Imager, State

logger = logging.getLogger(__name__)

router = APIRouter()
BlockState = Literal["", "moving", "capturing", "previewing"]
fast_refresh: asyncio.Event


class Message(BaseModel):
    msg: str
    t: float


class FCState(BaseModel):
    running: bool
    step: int
    msg: Message

    @classmethod
    def default(cls) -> FCState:
        return FCState(step=0, running=False, msg=Message(msg="", t=time.time()))


class WebState(State):
    fcs: tuple[FCState, FCState]
    block: BlockState
    msg: Message


message = "Idle"
state = WebState(
    **State.default().dict(),
    fcs=(FCState.default(), FCState.default()),
    block="",
    msg=Message(msg=message, t=time.time()),
)


def update_block(b: BlockState, fc: int | None = None) -> None:
    if fc is None:
        state.block = b
    else:
        state.fcs[fc].running = bool(b)
        state.fcs[fc].msg = Message(msg=b, t=time.time())
    try:
        if fast_refresh.is_set():
            ...
        else:
            fast_refresh.set()
            fast_refresh.clear()
    except AttributeError:
        ...


async def poll_state(ws: WebSocket) -> NoReturn:
    global fast_refresh, state
    imager: Imager = ws.app.state.imager
    fast_refresh = ws.app.state.fast_refresh

    while True:
        try:
            if fast_refresh.is_set():
                await asyncio.sleep(0.5)
            else:
                await asyncio.wait_for(fast_refresh.wait(), 5)
        except asyncio.TimeoutError:
            ...
        finally:
            try:
                # Do not put this in the argument for the copy line.
                # Otherwise the old state would be stored while awaiting the new state, resulting in old data overwriting the new.
                new_state = await imager.state
                state = state.copy(update=new_state.dict())
            except asyncio.CancelledError as e:
                raise e
            except BaseException as e:
                logger.error(f"Status error: {type(e).__name__}: {e}")
        await ws.send_json(jsonable_encoder(state))


@router.websocket("/status")
async def poll_msg(ws: WebSocket):
    """
    Get status every 5 seconds
    Sending responsibility is not mine

    Args:
      websocket (WebSocket): The websocket connection to the client.
      imager (Imager): Imager
      q_log (asyncio.Queue[str]): asyncio.Queue[str]
    """
    global message, state
    q_log: asyncio.Queue[str] = ws.app.state.q_log

    task = asyncio.create_task(poll_state(ws))
    await ws.accept()
    await ws.send_json(jsonable_encoder(state))

    try:
        while True:
            message = await q_log.get()
            state = state.copy(update={"msg": Message(msg=message, t=time.time())})
            # await asyncio.sleep(0.05)
            await ws.send_json(jsonable_encoder(state))
    except (WebSocketDisconnect, RuntimeError, ConnectionClosedOK):
        ...
    finally:
        task.cancel()
