from __future__ import annotations

import asyncio
import logging
from dataclasses import dataclass
from typing import Annotated, Literal, Optional

from .base.instruments_types import SerialPorts
from .fluidics.arm9chem import ARM9Chem
from .fluidics.pump import Pump
from .fluidics.valve import ReagentPorts, Valves
from .utils.utils import until

logger = logging.getLogger(__name__)

μL = Annotated[int | float, "μL"]
μLpermin = Annotated[int | float, "μL/min"]


@dataclass(frozen=True)
class Reagent:
    name: str
    port: ReagentPorts
    v_pull: int | float = 100
    v_prime: int | float = 250
    v_push: int | float = 2000
    wait: int | float = 26


class _FlowCell:
    @classmethod
    async def ainit(
        cls,
        name: Literal["A", "B"],
        ports: dict[SerialPorts, str],
        arm9chem: ARM9Chem,
        valves: Optional[Valves] = None,
        pump: Optional[Pump] = None,
    ) -> _FlowCell:
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
        if name not in ("A", "B"):
            raise ValueError("Invalid name.")

        self.name = name
        self.id_: Literal[0, 1] = 0 if self.name == "A" else 1
        self.v: Valves
        self.p: Pump
        self.arm9chem: ARM9Chem

    async def initialize(self) -> None:
        await asyncio.gather(self.v.initialize(), self.p.initialize())

    async def _flow(
        self,
        port: ReagentPorts,
        vol_barrel: μL = 250,
        *,
        v_pull: μLpermin = 250,
        v_push: μLpermin = 2000,
        wait: int | float = 26,
    ) -> None:
        async with self.arm9chem.shutoff_valve(), self.v.move(port):
            await self.p.pump(
                vol=self.steps_from_vol(vol_barrel),
                v_pull=self.sps_from_μLpermin(v_pull),
                v_push=self.sps_from_μLpermin(v_push),
                wait=wait,
            )

    async def prime(self, r: Reagent, vol_barrel: μL = 250):
        return await self._flow(r.port, vol_barrel, v_pull=r.v_prime)

    async def wash(self, r: Reagent, vol_barrel: μL = 250):
        return await self._flow(r.port, vol_barrel, v_pull=r.v_pull)

    @property
    async def temp(self) -> float:
        return await self.arm9chem.fc_temp(self.id_)

    async def set_temp(self, t: int | float) -> None:
        await self.arm9chem.set_fc_temp(self.id_, t)

    async def wait_temp(self, t: int | float, tol: int | float = 1, timeout: int = 60) -> None:
        async def temp_ok() -> bool:
            return abs(await self.temp - t) < tol

        await until(temp_ok, attempts=timeout)

    @staticmethod
    def steps_from_vol(vol: μL) -> int:
        """Per barrel."""
        if not 0 < vol <= 250:
            raise ValueError("Invalid barrel volume. Range is (0, 250] μL.")
        return int((vol / Pump.BARREL_VOL) * Pump.STEPS)

    @staticmethod
    def sps_from_μLpermin(speed: μLpermin) -> int:
        return int(_FlowCell.steps_from_vol(speed) / 60)


class FlowCells:
    @classmethod
    async def ainit(
        cls,
        ports: dict[SerialPorts, str],
    ) -> FlowCells:
        self = cls()
        arm9chem = await ARM9Chem.ainit(ports["arm9chem"])
        self.fcs = (
            await _FlowCell.ainit("A", ports, arm9chem),
            await _FlowCell.ainit("B", ports, arm9chem),
        )
        return self

    def __init__(self) -> None:
        self.fcs: tuple[_FlowCell, _FlowCell]

    def __getitem__(self, i: Literal[0, 1]) -> _FlowCell:
        return self.fcs[i]

    async def initialize(self) -> None:
        await asyncio.gather(self[0].initialize(), self[1].initialize())
