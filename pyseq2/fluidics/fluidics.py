from __future__ import annotations

import asyncio
import logging
from typing import Annotated, Literal, Optional, cast

from pyseq2.base.instruments_types import SerialPorts

from .arm9chem import ARM9Chem
from .pump import Pump
from .valve import ReagentPorts, Valves

logger = logging.getLogger(__name__)

μL = Annotated[int | float, "μL"]
μLpermin = Annotated[int | float, "μL/min"]


class Speed:
    FLUSH = 700
    PRIME = 100
    REAGENT = 40


class Fluidics:
    @classmethod
    async def ainit(
        cls,
        name: Literal["A", "B"],
        ports: dict[SerialPorts, str],
        arm9chem: ARM9Chem,
        valves: Optional[Valves] = None,
        pump: Optional[Pump] = None,
    ) -> Fluidics:
        if name not in ("A", "B"):
            raise ValueError("Invalid name.")

        self = cls(name)
        if valves is None:
            v = ("valve_a1", "valve_a2") if name == "A" else ("valve_b1", "valve_b2")
            valves = await Valves.ainit(name, ports[v[0]], ports[v[1]])
        if pump is None:
            p = "pumpa" if name == "A" else "pumpb"
            pump = await Pump.ainit(p, ports[p])

        self.v = valves
        self.p = pump
        self.arm9chem = arm9chem
        return self

    def __init__(self, name: Literal["A", "B"]) -> None:
        self.name = name
        self.v: Valves
        self.p: Pump
        self.arm9chem: ARM9Chem

    async def initialize(self) -> None:
        await asyncio.gather(self.v.initialize(), self.p.initialize(), self.arm9chem.initialize())

    async def maintenance_wash(self, port: ReagentPorts) -> None:
        async with self.arm9chem.shutoff_valve():
            await self.v.move(port)
            await self.p.pump(48000)
            await self.v.move(cast(ReagentPorts, 9))

    async def prime(self) -> None:
        ...

    # def vol_to_pos(self, vol: μL) -> int:
    #     return int(vol / self.vol_range[1] * self.STEPS)

    # def speed_to_sps(self, speed: μLpermin) -> int:
    #     return int(speed / self.vol_range[0] / 60)

    # @property
    # def vol_range(self) -> tuple[μL, μL]:
    #     hi = self.n_barrel * self.BARREL_VOL
    #     return hi / self.STEPS, hi

    # @property
    # def flow_range(self) -> tuple[μLpermin, μLpermin]:
    #     return self.vol_range[0] * 40 * 60, self.vol_range[0] * 8000 * 60

    # , n_barrel: Literal[1, 2, 4, 8] = 1
