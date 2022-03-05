from __future__ import annotations

import asyncio
import os
from logging import getLogger

import numpy as np
from fastapi import FastAPI
from fastapi.encoders import jsonable_encoder
from fastapi.middleware.cors import CORSMiddleware

from pyseq2 import FlowCells, Imager, get_ports

from .api_types import UserSettings
from .imaging import update_img
from .routers import mancommand, status, user

q_log: asyncio.Queue[str] = asyncio.Queue()
q_log2: asyncio.Queue[str] = asyncio.Queue()

logger = getLogger(__name__)


def gen_server():
    app = FastAPI()
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    async def setup_backend():
        try:
            ports = await get_ports(60)
        except RuntimeError as e:
            raise RuntimeError(
                f"Cannot find instrument {e.args[1]}. If you are running a fake HiSeq, make sure to add --fake to the run argument."
            )
        imager = await Imager.ainit(ports)
        fcs = await FlowCells.ainit(ports)

        app.state.imager = imager
        app.state.fcs = fcs
        app.state.q_log = q_log
        app.state.q_log2 = q_log2
        app.state.fast_refresh = asyncio.Event()
        app.state.user_settings = jsonable_encoder(UserSettings.default())
        app.state.img = update_img(np.random.randint(0, 256, (4, 128, 2048), dtype=np.uint8))

    app.on_event("startup")(setup_backend)
    app.include_router(status.router)
    app.include_router(user.router)
    app.include_router(mancommand.router)

    return app


# @app.get("/experiment/{fc}")
# async def download(fc: int):
#     resp = StreamingResponse(
#         io.StringIO(yaml.safe_dump(userSettings.exps[fc].to_experiment().dict(), sort_keys=False)),
#         media_type="application/yaml",
#     )
#     print(userSettings.exps[fc].to_experiment())
#     resp.headers["Content-Disposition"] = f"attachment; filename={userSettings.exps[fc].name}.yaml"
#     return resp


# @app.post("/experiment/{fc}")
# async def create_file(fc: bool, file: UploadFile):
#     f: IO[bytes] = file.file  # type: ignore
#     try:
#         y = yaml.safe_load(f)
#         print(y)
#         ne = NExperiment.from_experiment(Experiment.parse_obj(y), userSettings.max_uid)
#         ne.fc = fc
#         userSettings.max_uid += len(ne.reagents) + len(ne.cmds)
#         userSettings.exps[fc] = ne

#         q_user.put_nowait(None)
#     except BaseException as e:
#         raise HTTPException(400, detail=f"{type(e).__name__}: {e}")
#     return "ok"
