from __future__ import annotations

from typing import NoReturn

import numpy as np
from fastapi import APIRouter, Request, WebSocket, WebSocketDisconnect
from fastapi.encoders import jsonable_encoder
from websockets.exceptions import ConnectionClosedOK

from pyseq2.experiment import *
from pyseq2.imager import Imager
from pyseq2server.imaging import Img, update_img

from ..api_types import CommandResponse, UserSettings
from ..utils.utils import q_listener

router = APIRouter()
q_cmd: asyncio.Queue[CommandResponse | tuple[int, int, int]] = asyncio.Queue()


async def ret_cmd(ws: WebSocket) -> NoReturn:
    while True:
        res = await q_cmd.get()
        print(res)
        if isinstance(res, CommandResponse):
            to_send = res
        else:
            to_send = CommandResponse(step=res)

        print(f"sending {to_send}")
        await ws.send_json(jsonable_encoder(to_send))


@router.websocket("/cmd")
async def cmd_endpoint(ws: WebSocket) -> None:

    global latest, img
    await ws.accept()
    imager: Imager = ws.app.state.imager
    fcs: FlowCells = ws.app.state.fcs

    us = UserSettings.parse_obj(ws.app.state.user_settings)
    with q_listener(ret_cmd(ws)):
        try:
            while True:
                cmd = await ws.receive_text()
                print(cmd)
                try:
                    match cmd:
                        # TODO Need to block UI when moving.
                        case "move":
                            logger.info(f"")
                            await imager.move(x=0)
                        case "capture" | "preview" as c:
                            logger.info(c)
                            p = us.image_params.copy()
                            if c == "capture":
                                p.save = True
                                p.z_from, p.z_to = 0, 0
                            else:
                                p.save = False
                            new_image = await us.image_params.run(fcs, p.fc, imager, q_cmd)  # type: ignore
                            logger.info("Capture completed")
                            ws.app.state.img = update_img(new_image)
                            logger.info("Image updated")
                            # await asyncio.sleep(0.1)
                            q_cmd.put_nowait(CommandResponse(msg="imgReady"))  # Doesn't seem to send with 1.
                            q_cmd.put_nowait(CommandResponse(msg="imgReady"))

                            logger.info("ok_put")
                        case "autofocus":
                            logger.info(f"Autofocus")
                            await imager.autofocus()
                            q_cmd.put_nowait(CommandResponse(msg="ok"))
                        case "stop":
                            q_cmd.put_nowait(CommandResponse(msg="ok"))
                        case _ as x:
                            logger.error(f"What is this command {x}?")

                except BaseException as e:
                    q_cmd.put_nowait(CommandResponse(error=f"Error: {type(e).__name__}: {e}"))
                    q_cmd.put_nowait(CommandResponse(error=f"Error: {type(e).__name__}: {e}"))

        except (WebSocketDisconnect, RuntimeError, ConnectionClosedOK):
            ...


@router.get("/img", response_model=Img)
async def get_img(request: Request):
    return request.app.state.img
