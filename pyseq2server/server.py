from __future__ import annotations

import asyncio
from logging import getLogger

import numpy as np
from fastapi import FastAPI
from fastapi.encoders import jsonable_encoder
from fastapi.middleware.cors import CORSMiddleware

from pyseq2 import FlowCells, Imager, get_ports
from pyseq2.utils.coords import raw_to_mm

from .api_types import UserSettings
from .imaging import update_afimg, update_img
from .routers import mancommand, status, user

q_log: asyncio.Queue[str] = asyncio.Queue()
q_log2: asyncio.Queue[str] = asyncio.Queue()

logger = getLogger(__name__)


def gen_server(init: bool = True):
    app = FastAPI()
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    async def setup_backend(init: bool = True) -> None:
        try:
            ports = await get_ports()
        except RuntimeError as e:
            raise RuntimeError(
                f"Cannot find instrument {e.args[1]}. If you are running a fake HiSeq, make sure to add --fake to the run argument."
            )
        imager = await Imager.ainit(ports)
        fcs = await FlowCells.ainit(ports)

        if init:
            await asyncio.gather(imager.initialize(), fcs.initialize())

        app.state.imager = imager
        app.state.fcs = fcs
        app.state.q_log = q_log
        app.state.q_log2 = q_log2
        app.state.fast_refresh = asyncio.Event()

        state = await imager.state
        xy = tuple(round(x, 2) for x in raw_to_mm(False, x=state.x, y=state.y))
        user = UserSettings.default()
        user.image_params = user.image_params.copy(
            update=dict(
                xy0=xy,
                xy1=(xy[0], xy[1] - 0.7),
                laser_onoff=state.laser_onoff,
                lasers=state.lasers,
                od=state.od,
            )
        )

        app.state.user_settings = jsonable_encoder(user)
        app.state.img = update_img(
            np.random.randint(0, 4096, (4, 128, 2048), dtype=np.uint16), channels=(True, True, True, True)
        )
        app.state.afimg = update_afimg(
            np.random.randint(0, 4096, (259, 64, 256), dtype=np.uint16), laplacian=[0 for _ in range(259)]
        )

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
