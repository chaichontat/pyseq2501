from __future__ import annotations

import asyncio
from asyncio import CancelledError, Task
from contextlib import contextmanager
from logging import getLogger
from typing import Literal, NoReturn

from fastapi import APIRouter, Request, WebSocket, WebSocketDisconnect
from fastapi.encoders import jsonable_encoder
from pydantic import BaseModel
from websockets.exceptions import ConnectionClosedOK

from pyseq2 import FlowCells, Imager
from pyseq2server.imaging import Img, update_img

from ..api_types import CommandResponse, MoveManual, UserSettings
from ..utils.utils import q_listener

router = APIRouter()
QCmd = asyncio.Queue[CommandResponse | tuple[int, int, int]]

q_cmd: QCmd = asyncio.Queue()
logger = getLogger(__name__)


async def ret_cmd(ws: WebSocket) -> None:
    while True:
        try:
            res = await q_cmd.get()
            print(res)
            if isinstance(res, CommandResponse):
                to_send = res
            else:
                to_send = CommandResponse(step=res)

            print(f"sending {to_send}")
            await ws.send_json(jsonable_encoder(to_send))
        except CancelledError:
            break
        except BaseException as e:
            ws.app.state.q_log.put_nowait(f"Error: {type(e).__name__}: {e}")


class CommandWeb(BaseModel):
    move: MoveManual | None = None
    cmd: Literal["preview", "capture"] | None = None


@contextmanager
def cancel_wrapper(q_cmd: QCmd, q_log: asyncio.Queue[str], q_status: asyncio.Queue[bool]):
    q_status.put_nowait(True)
    try:
        yield
    except CancelledError:
        q_cmd.put_nowait(CommandResponse(error="Cancelled"))
    except BaseException as e:
        q_log.put_nowait(f"Error: {type(e).__name__}: {e}")
    finally:
        q_status.put_nowait(False)


async def meh():
    return


@router.websocket("/cmd")
async def cmd_endpoint(ws: WebSocket) -> None:
    await ws.accept()
    imager: Imager = ws.app.state.imager
    fcs: FlowCells = ws.app.state.fcs
    q_status: asyncio.Queue[bool] = ws.app.state.q_status
    q_log: asyncio.Queue[str] = ws.app.state.q_log

    async def cmd_image(cmd: CommandWeb):
        with cancel_wrapper(q_cmd, q_log, q_status):
            us = UserSettings.parse_obj(ws.app.state.user_settings)
            c = cmd.cmd
            p = us.image_params.copy()
            if c == "capture":
                p.save = True
                p.z_from, p.z_to = 0, 0
            else:
                p.save = False
            new_image = await us.image_params.run(fcs, p.fc, imager, q_cmd)  # type: ignore
            ws.app.state.img = update_img(new_image)
            q_cmd.put_nowait(CommandResponse(msg="imgReady"))  # Doesn't seem to send with 1.

    async def cmd_move(m: MoveManual):
        with cancel_wrapper(q_cmd, q_log, q_status):
            fc: bool = UserSettings.construct(**ws.app.state.user_settings).image_params["fc"]  # type: ignore
            await m.run(imager, fc)
            q_cmd.put_nowait(CommandResponse(msg="moveDone"))

    task: Task[None] = asyncio.create_task(meh())

    with q_listener(ret_cmd(ws)):
        try:
            while True:
                cmd = CommandWeb.parse_obj(await ws.receive_json())
                if cmd.cmd == "stop":
                    task.cancel()
                    q_status.put_nowait(True)
                    continue

                # if not task.done():
                #     q_cmd.put_nowait(CommandResponse(error=f"Old command still running: {task}."))
                #     continue

                if (cmd.cmd) is not None:
                    task = asyncio.create_task(cmd_image(cmd))

                if (m := cmd.move) is not None:
                    task = asyncio.create_task(cmd_move(m))

        except (WebSocketDisconnect, RuntimeError, ConnectionClosedOK):
            ...


@router.get("/img", response_model=Img)
async def get_img(request: Request):
    return request.app.state.img
