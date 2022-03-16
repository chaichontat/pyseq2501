from __future__ import annotations

import asyncio
import logging
from typing import Annotated, Literal, Optional, Type, TypeVar

from .base.instruments_types import SerialPorts
from .config import CONFIG
from .fluidics.arm9chem import ARM9Chem
from .fluidics.pump import Pump
from .fluidics.valve import Valves
from .utils.log import init_log
from .utils.utils import Singleton

logger = logging.getLogger(__name__)

μL = Annotated[float, "μL"]
μLpermin = Annotated[float, "μL/min"]
Seconds = Annotated[float, "s"]

T = TypeVar("T")

BPL = CONFIG.barrels_per_lane
MAX_SPEED = 2000 * BPL  # TODO: Verify
MAX_VOL = Pump.BARREL_VOL * BPL


class AFlowCell:
    @classmethod
    async def ainit(
        cls: Type[T],
        name: Literal["A", "B"],
        ports: dict[SerialPorts, str],
        arm9chem: ARM9Chem,
        valves: Optional[Valves] = None,
        pump: Optional[Pump] = None,
    ) -> T:
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
        self.lock = asyncio.Lock()

    async def initialize(self) -> None:
        async with self.lock:
            for i, f in enumerate((self.v.initialize(), self.p.initialize()), 1):
                await f
                logger.info(f"Flowcell {self.name} init [{i}/2] completed.")

    async def flow(
        self,
        port: int,
        vol: μL = 250,
        *,
        v_pull: μLpermin = 250,
        v_push: μLpermin = 2000,
        wait: Seconds = 26,
    ) -> None:

        if port not in CONFIG.enabled_ports:
            raise ValueError("Invalid port number.")

        async with self.arm9chem.shutoff_valve(), self.v.move_port(port), self.lock:
            await self.p.pump(
                vol=self.steps_from_vol(vol),
                v_pull=self.sps_from_μLpermin(v_pull),
                v_push=self.sps_from_μLpermin(v_push),
                wait=wait,
            )

    @property
    async def temp(self) -> float:
        return await self.arm9chem.fc_temp(self.id_)

    async def set_temp(self, t: float) -> None:
        await self.arm9chem.set_fc_temp(self.id_, t)

    async def temp_ok(self, t: float, tol: float = 1) -> bool:
        return abs(await self.temp - t) < tol

    @staticmethod
    def steps_from_vol(vol: μL) -> int:
        """Per Lane."""
        if not 0 < vol <= MAX_VOL:
            raise ValueError(f"Invalid volume. Range is (0, {MAX_VOL}] μL for {BPL} barrels/lane.")
        return int((vol / MAX_VOL) * Pump.STEPS)

    @staticmethod
    def sps_from_μLpermin(speed: μLpermin) -> int:
        if not 0 < speed <= MAX_SPEED:
            raise ValueError(f"Invalid speed. Range is (0, {MAX_SPEED}] μL/min for {BPL} barrels/lane.")
        return int((speed / MAX_VOL) * Pump.STEPS / 60)


class FlowCells(metaclass=Singleton):
    @classmethod
    async def ainit(
        cls,
        ports: dict[SerialPorts, str],
    ) -> FlowCells:
        self = cls()
        self.arm9chem = await ARM9Chem.ainit(ports["arm9chem"])
        self.fcs = (
            await AFlowCell.ainit("A", ports, self.arm9chem),
            await AFlowCell.ainit("B", ports, self.arm9chem),
        )
        return self

    def __init__(self) -> None:
        self.arm9chem: ARM9Chem
        self.fcs: tuple[AFlowCell, AFlowCell]

    def __getitem__(self, i: Literal[0, 1]) -> AFlowCell:
        return self.fcs[i]

    def __getattr__(self, s_: str) -> AFlowCell:
        match s_:
            case "A" | "a":
                return self.fcs[0]
            case "B" | "b":
                return self.fcs[1]
            case _:
                raise AttributeError(f"No attribute {s_}.")

    @init_log(logger, info=True)
    async def initialize(self) -> None:
        await asyncio.gather(self[0].initialize(), self[1].initialize(), self.arm9chem.initialize())
