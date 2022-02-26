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


class FCState(BaseModel):
    state: Literal["idle", "running"]
    step: int


class WebState(State):
    msg: str


message = "Idle"
state = WebState(**State.default().dict(), msg=message)


async def poll(ws: WebSocket) -> NoReturn:
    imager: Imager = ws.app.state.imager
    q_status: asyncio.Queue[bool] = ws.app.state.q_status

    global state
    send_now = False
    while True:
        try:
            await asyncio.wait_for(q_status.get(), 5)
        except asyncio.TimeoutError:
            send_now = False
        else:
            send_now = True
        finally:
            if raw := await imager.state:
                state = WebState(**raw.dict(), msg=message)
            else:
                state.msg = "Error: timeout on state retrieval."
            if send_now:
                await ws.send_json(jsonable_encoder(state))
                send_now = False


@router.websocket("/status")
async def poll_status(ws: WebSocket):
    """
    Get status every 5 seconds

    Args:
      websocket (WebSocket): The websocket connection to the client.
      imager (Imager): Imager
      q_log (asyncio.Queue[str]): asyncio.Queue[str]
    """
    global message
    q_log: asyncio.Queue[str] = ws.app.state.q_log

    task = asyncio.create_task(poll(ws))
    await ws.accept()
    await ws.send_json(jsonable_encoder(state))

    try:
        while True:
            try:
                message = await asyncio.wait_for(q_log.get(), 5)
                state.msg = message
            except asyncio.TimeoutError:
                ...
            finally:
                await ws.send_json(jsonable_encoder(state))
    except (WebSocketDisconnect, RuntimeError, ConnectionClosedOK):
        ...
    finally:
        task.cancel()
