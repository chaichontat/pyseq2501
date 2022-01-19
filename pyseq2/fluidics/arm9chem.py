from __future__ import annotations

import asyncio
import logging
from contextlib import asynccontextmanager
from typing import AsyncGenerator, Callable, Literal, ParamSpec, TypeVar

from pyseq2.base.instruments import UsesSerial
from pyseq2.com.async_com import COM, CmdParse
from pyseq2.utils.utils import chkrng, ok_if_match, ok_re, λ_float, λ_int

logger = logging.getLogger(__name__)

CHILLER_RANGE = (0.1, 20.0)
FC_RANGE = (0.0, 65.0)

P = ParamSpec("P")
T = TypeVar("T")


def check01(f: Callable[P, T]) -> Callable[P, T]:
    return chkrng(f, 0, 1)


# fmt: off
class ARM9Cmd:
    INIT        = CmdParse("INIT", ok_if_match(("A1", "N1")))
    GET_VERSION = CmdParse("?IDN", ok_re(r"Illumina,Bruno Fluidics Controller,0,v2\.[\d+]:A1"))
    GET_FC_TEMP = CmdParse(λ_float(lambda i: f"?FCTEMP:{i}"), ok_re(r"[\.\d]+C:A1", float))
    GET_CHILLER_TEMP = CmdParse(
        "?RETEMP:3",
        ok_re(r"(\d\.\d{3})C:(\d\.\d{3})C:(\d\.\d{3}):A1", lambda a, b, c: (float(a), float(b), float(c))),
    )
    GET_SHUTOFF_VALVE = CmdParse("?asyphon:0", ok_re(r"([01]):A1"))
    SET_SHUTOFF_VALVE = CmdParse(λ_int(check01(lambda i: f"asyphon:0:{i}")), ok_if_match("A1"))


    FC_OFF        = CmdParse(λ_int(check01(lambda i:     f"FCTEC:{i}:0")), ok_if_match("A1"))
    FC_ON         = CmdParse(λ_int(check01(lambda i:     f"FCTEC:{i}:1")), ok_if_match("A1"))
    SET_FC_PIDSF  = CmdParse(check01(lambda i, param, v: f"FCTEMP:{i}:{param}:{v}"), ok_if_match("A1"))
    SET_TEC_PIDSF = CmdParse(chkrng(lambda i, param, v:  f"RETEC:{i}:{param}:{v}", 0, 2), ok_if_match("A1"))
    
    SET_FC_TEMP   = CmdParse(λ_float(chkrng(lambda i, x: f"FCTEMP:{i}:{x}", *FC_RANGE)), ok_if_match("A1"))
    SET_CHILLER_TEMP = CmdParse(
        λ_float(chkrng(lambda i, x: f"RETEMP:{i}:{x}", *CHILLER_RANGE)), ok_if_match("A1")
    )
    SET_VACUUM    = CmdParse(λ_int(check01(lambda i: f"VACUUM:{i}")), ok_if_match("A1"))
# fmt: on


class ARM9Chem(UsesSerial):
    FC_PIDSF = ((0.2, 0.1, 0.0, 1.875, 6.0), (0.2, 0.1, 0.0, 1.875, 6.0))
    TEC_PIDSF = ((0.8, 0.2, 0.0, 1.875, 6.0), (0.8, 0.2, 0.0, 1.875, 6.0), (1.7, 1.1, 0.0))

    @classmethod
    async def ainit(cls, port_tx: str) -> ARM9Chem:
        self = cls()
        self.com = await COM.ainit("arm9chem", port_tx)
        return self

    def __init__(self) -> None:
        self.com: COM

    async def initialize(self) -> None:
        async with self.com.big_lock:
            logger.info("Initializing temperature control.")
            await self.com.send(ARM9Cmd.INIT)
            fc = (
                self.com.send(ARM9Cmd.SET_FC_PIDSF(i, param, v))
                for i in range(2)
                for param, v in zip("PIDSF", self.FC_PIDSF[i])
            )
            tec = (
                self.com.send(ARM9Cmd.SET_TEC_PIDSF(i, param, v))
                for i in range(3)
                for param, v in zip("PIDSF", self.TEC_PIDSF[i])
            )
            await asyncio.gather(*fc, *tec)
            await asyncio.gather(*(self.com.send(ARM9Cmd.FC_OFF(i)) for i in (0, 1)))
            logger.info("Temperature control initialized.")

    async def fc_temp(self, i: Literal[0, 1]) -> float:
        return await self.com.send(ARM9Cmd.GET_FC_TEMP(i))

    async def chiller_temp(self, i: Literal[0, 1, 2]) -> tuple[float, float, float]:
        return await self.com.send(ARM9Cmd.GET_CHILLER_TEMP)

    async def set_fc_temp(self, i: Literal[0, 1], t: int | float) -> None:
        await self.com.send(ARM9Cmd.FC_ON(i))
        await self.com.send(ARM9Cmd.SET_FC_TEMP(i, t))

    async def set_chiller_temp(self, i: Literal[0, 1, 2], t: int | float) -> None:
        await self.com.send(ARM9Cmd.SET_CHILLER_TEMP(i, t))

    async def set_vacuum(self, onoff: bool) -> None:
        await self.com.send(ARM9Cmd.SET_VACUUM(onoff))

    @asynccontextmanager
    async def shutoff_valve(self) -> AsyncGenerator[None, None]:
        try:
            await self.com.send(ARM9Cmd.SET_SHUTOFF_VALVE(1))
            yield
        finally:
            await self.com.send(ARM9Cmd.SET_SHUTOFF_VALVE(0))
