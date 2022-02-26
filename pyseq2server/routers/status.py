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
    wait_time = 5
    send_now = False
    while True:
        try:
            running = await asyncio.wait_for(q_status.get(), wait_time)
        except asyncio.TimeoutError:
            ...
        else:
            if running:
                send_now = True
                wait_time = 0.5
            else:
                send_now = False
                wait_time = 5
        finally:
            try:
                state = WebState(**(await imager.state).dict(), msg=message)
            except BaseException as e:
                state.msg = f"Error: {type(e).__name__}: {e}"

            if send_now:
                await ws.send_json(jsonable_encoder(state))


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
