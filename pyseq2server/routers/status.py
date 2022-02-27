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
    while True:
        try:
            running = await asyncio.wait_for(q_status.get(), wait_time)
        except asyncio.TimeoutError:
            ...
        else:
            if running:
                wait_time = 0.5
            else:
                wait_time = 5
        finally:
            try:
                state = WebState(**(await imager.state).dict(), msg=message)
            except TimeoutError:
                ...
            except asyncio.CancelledError as e:
                raise e
            except BaseException as e:
                logger.error(f"Status error: {type(e).__name__}: {e}")
                # state.msg = f"Status error: {type(e).__name__}: {e}

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
            message = await q_log.get()
            state.msg = message
            await ws.send_json(jsonable_encoder(state))
    except (WebSocketDisconnect, RuntimeError, ConnectionClosedOK):
        ...
    finally:
        task.cancel()
