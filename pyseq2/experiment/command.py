#%%
from __future__ import annotations

import asyncio
import math
from logging import getLogger
from pathlib import Path
from typing import Annotated, Literal, Protocol, cast

import numpy as np
from pydantic import BaseModel, Field

from .reagent import Reagent
from pyseq2.flowcell import FlowCells, Seconds, μL
from pyseq2.imager import Imager
from pyseq2.utils import coords

logger = getLogger(__name__)
#%%
class AbstractCommand(Protocol):
    op: str

    async def run(self, fcs: FlowCells, i: Literal[0, 1], imager: Imager) -> None:
        ...


async def pump_prime(fcs: FlowCells, i: Literal[0, 1], cmd: Pump | Prime):
    if not isinstance(r := cmd.reagent, Reagent):
        raise ValueError(
            "Individual command needs an actual Reagent, not its name. To fix: cmd.reagent = reagents[name]."
        )

    fc = fcs[i]
    match cmd.op:
        case "prime":
            await fc.flow(r.port, cmd.volume, v_pull=r.v_prime, v_push=r.v_push, wait=r.wait)
        case "pump":
            await fc.flow(r.port, cmd.volume, v_pull=r.v_pull, v_push=r.v_push, wait=r.wait)
        case _:
            raise ValueError("Invalid command.")


class Pump(BaseModel):
    reagent: str
    volume: μL = 250
    op: Literal["pump"] = "pump"

    async def run(self, fcs: FlowCells, i: Literal[0, 1], imager: Imager) -> None:
        await pump_prime(fcs, i, self)


class Prime(BaseModel):
    reagent: str
    volume: μL = 250
    op: Literal["prime"] = "prime"

    async def run(self, fcs: FlowCells, i: Literal[0, 1], imager: Imager) -> None:
        await pump_prime(fcs, i, self)


class Temp(BaseModel):
    temp: int | float
    wait: bool = False
    op: Literal["temp"] = "temp"

    async def run(self, fcs: FlowCells, i: Literal[0, 1], imager: Imager) -> None:
        await fcs[i].set_temp(self.temp)


class Hold(BaseModel):
    time: Seconds
    temp: float
    op: Literal["hold"] = "hold"

    async def run(self, fcs: FlowCells, i: Literal[0, 1], imager: Imager) -> None:
        await asyncio.sleep(self.time)


class Autofocus(BaseModel):
    channel: Literal[0, 1, 2, 3]
    op: Literal["autofocus"] = "autofocus"

    async def run(self, fcs: FlowCells, i: Literal[0, 1], imager: Imager) -> None:
        await imager.autofocus(self.channel)


class TakeImage(BaseModel):
    name: str
    path: str
    xy0: tuple[float, float]
    xy1: tuple[float, float]
    overlap: float
    channels: tuple[bool, bool, bool, bool]
    z_tilt: int | tuple[int, int, int]
    z_obj: int
    laser_onoff: tuple[bool, bool]
    lasers: tuple[int, int]
    flowcell: bool
    od: tuple[float, float]
    save: bool
    z_spacing: int = 0
    z_n: int = 1
    op: Literal["image"] = "image"

    def calc_pos(self) -> tuple[int, int, list[int], list[int]]:
        n_bundles = math.ceil(max(self.xy0[1], self.xy1[1]) - (min(self.xy0[1], self.xy1[1])) / 0.048)
        fc = cast(Literal[0, 1], int(self.flowcell))
        y_start = coords.mm_to_raw(fc, y=min(self.xy0[1], self.xy1[1]))

        x_step = self.overlap * 0.768
        x_n = math.ceil((max(self.xy0[0], self.xy1[0]) - (x_start := min(self.xy0[0], self.xy1[0]))) / x_step)

        xs = [coords.mm_to_raw(fc, x=x_start + n * x_step) for n in range(x_n)]
        zs = [self.z_obj + n * self.z_spacing for n in range(self.z_n)]

        return n_bundles, y_start, xs, zs

    async def run(self, fcs: FlowCells, i: Literal[0, 1], imager: Imager) -> None:
        logger.info("Taking images.")
        n_bundles, y_start, xs, zs = self.calc_pos()

        channels = cast(
            frozenset[Literal[0, 1, 2, 3]], frozenset(i for i, c in enumerate(self.channels) if c)
        )

        path = Path(self.path) / self.name
        paths = [path.parent / f"{path.stem}_{i}.tif" for i in range(len(xs))]
        # Test if we can write to the directory
        if self.save:
            [p.touch() for p in paths]

        big_img = np.empty((len(zs), len(channels), 128 * n_bundles), dtype=np.uint16)
        for p, x in zip(paths, xs):
            for idx, z in enumerate(zs):
                await imager.move(x=x, y=y_start, z_obj=z, z_tilt=self.z_tilt)
                img, state = await imager.take(n_bundles, channels=channels)
                big_img[idx] = img
            if self.save:
                imager.save(p, big_img)  # TODO state per each stack.

        logger.info("Done taking images.")


class Goto(BaseModel):
    step: int
    n: int
    op: Literal["goto"] = "goto"


Cmd = Annotated[Pump | Prime | Temp | Hold | Autofocus | TakeImage | Goto, Field(discriminator="op")]
