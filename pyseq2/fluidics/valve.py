from __future__ import annotations

import asyncio
import logging
import time
from contextlib import asynccontextmanager
from typing import Literal, cast, get_args

from pyseq2.base.instruments import Movable, UsesSerial
from pyseq2.base.instruments_types import ValveName
from pyseq2.com.async_com import COM, CmdParse
from pyseq2.utils.utils import ok_re, λ_int

logger = logging.getLogger(__name__)
ValvePorts = Literal[1, 2, 3, 4, 5, 6, 7, 8, 9, 10]
ReagentPorts = Literal[1, 2, 3, 4, 5, 6, 7, 8, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19]


# fmt: off
class ValveCmd:
    ID          = CmdParse("ID", ok_re(r"ID = (.+)", lambda x: x))
    SET_POS     = λ_int(lambda x: f"GO{x}")
    GET_POS     = CmdParse("CP", ok_re(r"Position is  = (\d+)", int))
    GET_N_PORTS = CmdParse("NP", ok_re(r"NP = (\d+)", int))
# fmt: on


class _Valve(Movable, UsesSerial):
    @classmethod
    async def ainit(cls, name: ValveName, port_tx: str) -> _Valve:
        self = cls(name)
        self.com = await COM.ainit(name, port_tx)  # VICI hates \n 🙄.
        return self

    def __init__(self, name: ValveName) -> None:
        self.com: COM
        self.name = name
        self.t_lastcmd = 0.0

    async def initialize(self) -> None:
        async with self.com.big_lock:
            logger.info(f"Initializing {self.name}.")
            if (id_ := await self.com.send(ValveCmd.ID)) != "not used":
                raise Exception(f"ID for {self.name} is {id_}. Need to add prefix.")
            # All valves seem to have 10 ports (at least on the 2000).
            assert await self.com.send(ValveCmd.GET_N_PORTS) == 10
            logger.info(f"{self.name} initialized.")

    @property
    async def pos(self) -> ValvePorts:
        p = await self.com.send(ValveCmd.GET_POS)
        assert p in get_args(ValvePorts)
        return cast(ValvePorts, p)

    async def move(self, p: ValvePorts) -> None:
        # If pos is the same as current position, will get `GO${p} = Bad command` as return.
        async with self.com.big_lock:  # Possible for valve to change after awaiting self.pos.
            if time.time() - self.t_lastcmd < 10.0:
                logger.warning(
                    "Time between valve moves is less than 10 seconds. Illumina does not like this."
                )
            if await self.pos == p:
                return
            await self.com.send(ValveCmd.SET_POS(p))
            self.t_lastcmd = time.time()
            if await self.pos != p:
                raise Exception(f"Port {self.name} did not move to {p}.")


class Valves(Movable):
    @classmethod
    async def ainit(cls, name: Literal["A", "B"], port1: str, port2: str) -> Valves:
        self = cls(name)
        match name:
            case "A":
                self.v = (await _Valve.ainit("valve_a1", port1), await _Valve.ainit("valve_a2", port2))
            case "B":
                self.v = (await _Valve.ainit("valve_b1", port1), await _Valve.ainit("valve_b2", port2))
        return self

    def __init__(self, name: Literal["A", "B"]) -> None:
        self.v: tuple[_Valve, _Valve]
        self.name = name
        self.lock = asyncio.Lock()

    def __getitem__(self, i: Literal[0, 1]) -> _Valve:
        return self.v[i]

    async def initialize(self) -> None:
        async with self.lock:
            await asyncio.gather(self.v[0].initialize(), self.v[1].initialize())

    @property
    async def pos(self) -> int:
        p1, p2 = await asyncio.gather(self[0].pos, self[1].pos)
        if p1 == 10:
            return p2 + 9
        return p1

    async def _move(self, p: ReagentPorts) -> None:
        # if self.lock.locked():
        #     raise Exception("Do not send multiple move commands at once.")

        async with self.lock:
            if not 1 <= p <= 18 and p != 9:
                raise ValueError("Invalid port number. Range is [1, 18], excluding 9.")
            if p > 9:
                await asyncio.gather(self[0].move(10), self[1].move(cast(ValvePorts, p - 9)))
            else:
                await self[0].move(cast(ValvePorts, p))
            assert await self.pos == p

    @asynccontextmanager
    async def move(self, pos: ReagentPorts):
        try:
            await self._move(pos)
            yield
        finally:
            await self._move(cast(ReagentPorts, 9))  # "Safe" position.
