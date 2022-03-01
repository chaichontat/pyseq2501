from __future__ import annotations

import asyncio
from asyncio import CancelledError, Task
from contextlib import contextmanager
from logging import getLogger
from typing import Any, Literal, NoReturn

from fastapi import APIRouter, Request, WebSocket, WebSocketDisconnect
from fastapi.encoders import jsonable_encoder
from pydantic import BaseModel
from websockets.exceptions import ConnectionClosedOK

from pyseq2 import FlowCells, Imager
from pyseq2.experiment import Experiment
from pyseq2server.imaging import Img, update_img
from pyseq2server.routers.status import update_block

from ..api_types import CommandResponse, MoveManual, NExperiment, UserSettings
from ..utils.utils import q_listener

router = APIRouter()
QCmd = asyncio.Queue[CommandResponse | tuple[int, int, int]]

q_cmd: QCmd = asyncio.Queue()
logger = getLogger(__name__)


async def ret_cmd(ws: WebSocket) -> None:
    while True:
        try:
            res = await q_cmd.get()
            if isinstance(res, CommandResponse):
                to_send = res
            else:
                to_send = CommandResponse(step=res)
            await ws.send_json(jsonable_encoder(to_send))
        except CancelledError:
            break
        except BaseException as e:
            logger.error(f"Error in ret_cmd: {e}")
            raise e
            # ws.app.state.q_log.put_nowait(f"Error: {type(e).__name__}: {e}")


class FCCmd(BaseModel):
    fc: bool
    cmd: Literal["start", "validate", "stop"]


class CommandWeb(BaseModel):
    move: MoveManual | None = None
    cmd: Literal["preview", "capture"] | None = None
    fccmd: FCCmd | None = None


@contextmanager
def cancel_wrapper(q_cmd: QCmd, q_log: asyncio.Queue[str], fast_refresh: asyncio.Event):
    fast_refresh.set()
    try:
        yield
    except BaseException as e:
        logger.error(f"Error: {type(e).__name__}: {e}")
        raise e
    finally:
        fast_refresh.clear()
        update_block("")


async def meh():
    return


@router.websocket("/cmd")
async def cmd_endpoint(ws: WebSocket) -> None:
    await ws.accept()
    imager: Imager = ws.app.state.imager
    fcs: FlowCells = ws.app.state.fcs
    fast_refresh: asyncio.Event = ws.app.state.fast_refresh
    q_log: asyncio.Queue[str] = ws.app.state.q_log

    async def cmd_image(cmd: CommandWeb):
        with cancel_wrapper(q_cmd, q_log, fast_refresh):
            us = UserSettings.parse_obj(ws.app.state.user_settings)
            c = cmd.cmd
            update_block("capturing" if c == "capture" else "previewing")
            p = us.image_params.copy()
            if c == "capture":
                p.save = True
            else:
                p.save = False
                p.z_from, p.z_to = 0, 0
            new_image = await p.run(fcs, p.fc, imager, q_cmd)  # type: ignore
            ws.app.state.img = update_img(new_image)
            q_cmd.put_nowait(CommandResponse(msg="imgReady"))  # Doesn't seem to send with 1.
            q_cmd.put_nowait(CommandResponse(msg="imgReady"))  # Doesn't seem to send with 1.

    async def cmd_move(m: MoveManual):
        with cancel_wrapper(q_cmd, q_log, fast_refresh):
            fc: bool = UserSettings.construct(**ws.app.state.user_settings).image_params["fc"]  # type: ignore
            await m.run(imager, fc)

    async def cmd_validate(fc: bool) -> Experiment:
        with cancel_wrapper(q_cmd, q_log, fast_refresh):
            out = NExperiment(**UserSettings.construct(**ws.app.state.user_settings).exps[fc]).to_experiment()  # type: ignore
            q_log.put_nowait("Validation successful.")
        return out

    async def cmd_run_exp(fc: bool):
        exp = await cmd_validate(fc)
        with cancel_wrapper(q_cmd, q_log, fast_refresh):
            await exp.run(fcs, fc, imager, q_cmd)
            

    task: Task[Any] = asyncio.create_task(meh())
    fc_tasks: list[Task[Any]] = [asyncio.create_task(meh()), asyncio.create_task(meh())]

    with q_listener(ret_cmd(ws)):
        try:
            while True:
                cmd = CommandWeb.parse_obj(await ws.receive_json())
                print(cmd)
                if cmd.cmd == "stop":
                    logger.warning("Received stop signal.")
                    task.cancel()
                    continue

                if not task.done():
                    q_cmd.put_nowait(CommandResponse(error=f"Old command still running: {task}."))
                    continue

                match cmd:
                    case CommandWeb(cmd="capture") | CommandWeb(cmd="preview"):
                        task = asyncio.create_task(cmd_image(cmd))
                    case CommandWeb(fccmd=FCCmd(fc=fc, cmd="validate")):
                        task = asyncio.create_task(cmd_validate(fc))
                    case CommandWeb(fccmd=FCCmd(fc=fc, cmd="start")):
                        fc_tasks[fc] = asyncio.create_task(cmd_run_exp(fc))
                    case CommandWeb(fccmd=FCCmd(fc=fc, cmd="stop")):
                        fc_tasks[fc].cancel()
                    case _:
                        ...

                if (m := cmd.move) is not None:
                    task = asyncio.create_task(cmd_move(m))
                    continue

        except (WebSocketDisconnect, RuntimeError, ConnectionClosedOK):
            ...


@router.get("/img", response_model=Img)
async def get_img(request: Request):
    return request.app.state.img
