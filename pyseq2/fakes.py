from __future__ import annotations

import asyncio
from contextlib import asynccontextmanager
from logging import getLogger
from pathlib import Path
from typing import AsyncGenerator, Literal, Optional, Type, TypeVar

import numpy as np

from pyseq2.base.instruments_types import SerialPorts
from pyseq2.flowcell import AFlowCell, FlowCells, Seconds, μL, μLpermin
from pyseq2.fluidics.arm9chem import ARM9Chem
from pyseq2.fluidics.pump import Pump
from pyseq2.fluidics.valve import Valves
from pyseq2.imager import Imager, Position, State
from pyseq2.imaging.camera.dcam import UInt16Array
from pyseq2.imaging.ystage import YStage
from pyseq2.utils.ports import FAKE_PORTS

logger = getLogger(__name__)

T = TypeVar("T")


class FakeARM9Chem(ARM9Chem):
    @classmethod
    async def ainit(cls, port_tx: str) -> FakeARM9Chem:
        return cls()

    def __init__(self) -> None:
        ...

    async def initialize(self) -> None:
        ...

    async def fc_temp(self, i: Literal[0, 1]) -> float:
        return 25.0

    async def chiller_temp(self, i: Literal[0, 1, 2]) -> tuple[float, float, float]:
        return (25.0, 25.0, 25.0)

    async def set_fc_temp(self, i: Literal[0, 1], t: int | float) -> None:
        ...

    async def set_chiller_temp(self, i: Literal[0, 1, 2], t: int | float) -> None:
        ...

    async def set_vacuum(self, onoff: bool) -> None:
        ...

    @asynccontextmanager
    async def shutoff_valve(self) -> AsyncGenerator[None, None]:
        try:
            yield
        finally:
            ...


class FakeFlowCell(AFlowCell):
    @classmethod
    async def ainit(
        cls: Type[T],
        name: Literal["A", "B"],
        ports: dict[SerialPorts, str],
        arm9chem: ARM9Chem,
        valves: Optional[Valves] = None,
        pump: Optional[Pump] = None,
    ) -> T:
        return cls(name)

    def __init__(self, name: Literal["A", "B"]) -> None:
        ...

    async def initialize(self) -> None:
        ...

    async def flow(
        self,
        port: int,
        vol_barrel: μL = 250,
        *,
        v_pull: μLpermin = 250,
        v_push: μLpermin = 2000,
        wait: Seconds = 26,
    ) -> None:
        ...

    @property
    async def temp(self) -> float:
        return 25.0

    async def set_temp(self, t: int | float) -> None:
        ...

    async def temp_ok(self, t: int | float, tol: int | float = 1) -> bool:
        return True


class FakeFlowCells(FlowCells):
    @classmethod
    async def ainit(
        cls,
        ports: dict[SerialPorts, str],
    ) -> FlowCells:
        self = cls()
        arm9chem = await FakeARM9Chem.ainit(FAKE_PORTS["arm9chem"])
        self.fcs = (
            await FakeFlowCell.ainit("A", ports, arm9chem),
            await FakeFlowCell.ainit("B", ports, arm9chem),
        )
        return self

    def __init__(self) -> None:
        self.fcs: tuple[FakeFlowCell, FakeFlowCell]

    def __getitem__(self, i: Literal[0, 1]) -> FakeFlowCell:
        return self.fcs[i]

    async def initialize(self) -> None:
        await asyncio.gather(self[0].initialize(), self[1].initialize())


class FakeImager(Imager):
    @classmethod
    async def ainit(cls, ports: dict[SerialPorts, str], init_cam: bool = True) -> FakeImager:
        return cls()

    def __init__(self) -> None:
        ...

    async def initialize(self) -> None:
        ...

    @property
    async def pos(self) -> Position:
        return Position.default()

    @property
    async def state(self) -> State:
        return State.default()

    async def wait_ready(self) -> None:
        ...

    async def move(
        self,
        *,
        x: Optional[int] = None,
        y: Optional[int] = None,
        z_obj: Optional[int] = None,
        z_tilt: Optional[int | tuple[int, int, int]] = None,
    ) -> None:
        ...

    async def take(
        self,
        n_bundles: int,
        dark: bool = False,
        channels: frozenset[Literal[0, 1, 2, 3]] = frozenset((0, 1, 2, 3)),
        move_back_to_start: bool = True,
        event_queue: Optional[asyncio.Queue[int]] = None,
    ) -> tuple[UInt16Array, State]:

        if event_queue:
            for i in range(n_bundles):
                event_queue.put_nowait(i)
        return (
            np.random.randint(0, 4096, (len(channels), n_bundles * 128, 2048), dtype=np.uint16),
            State.default(),
        )

    @staticmethod
    def calc_delta_pos(n_px_y: int) -> int:
        return int(n_px_y * Imager.UM_PER_PX * YStage.STEPS_PER_UM)

    async def autofocus(self, channel: Literal[0, 1, 2, 3] = 1) -> tuple[int, UInt16Array]:
        return 30000, np.ones((232, 5), dtype=np.uint16)

    @staticmethod
    def save(path: str | Path, img: UInt16Array, state: Optional[State] = None) -> None:
        ...
