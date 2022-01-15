import asyncio
from contextlib import asynccontextmanager
from logging import getLogger
from typing import Any, AsyncGenerator, Awaitable, Callable, Coroutine

from pyseq2.base.instruments import FPGAControlled, Movable
from pyseq2.com.async_com import CmdParse
from pyseq2.utils.utils import chkrng, ok_if_match, ok_re

logger = getLogger(__name__)


Y_OFFSET = int(7e6)
RANGE = (0, 65535)


class ObjCmd:
    # fmt: off
    # Callable[[Annotated[int, "mm/s"]], str]
    SET_VELO = CmdParse(lambda x: f"ZSTEP {int(1288471 * x)}", ok_if_match("ZSTEP"))
    SET_POS  = CmdParse(chkrng(lambda x: f"ZDACW {x}", *RANGE), ok_if_match("ZDACW"))
    GET_TARGET_POS = CmdParse(     "ZDACR"              , ok_re(r"^ZDACR (\d+)$", int))  # D A
    GET_POS        = CmdParse(     "ZADCR"              , ok_re(r"^ZADCR (\d+)$", int))  # A D
    
    # Autofocus stuffs
    SET_TRIGGER = CmdParse(lambda x: f"ZTRG {x}"   , ok_if_match("ZTRG"))
    ARM_TRIGGER = CmdParse(           "ZYT 0 3"    , ok_if_match("ZYT"))
    Z_MOVE      = CmdParse(lambda x: f"ZMV {x}"    , ok_if_match("@LOG Trigger Camera\nZMV"), n_lines=2)
    SWYZ        = CmdParse(           "SWYZ_POS 1" , ok_if_match("SWYZ_POS"))
    # fmt: on


class ZObj(FPGAControlled, Movable):
    STEPS_PER_UM = 262
    RANGE = (0, 65535)
    HOME = 65535

    cmd = ObjCmd

    async def initialize(self) -> bool | None:
        return await self.com.send(ObjCmd.SET_VELO(5))

    @property
    async def pos(self) -> int | None:
        return await self.com.send(ObjCmd.GET_POS)

    async def move(self, x: int) -> bool:
        return await self.com.send(ObjCmd.SET_POS(x))

    @asynccontextmanager
    async def af_arm(self, z_min: int = 2621, z_max: int = 60292) -> AsyncGenerator[Awaitable[Any], None]:
        try:
            await self.com.send(ObjCmd.SET_POS(z_max))  # Returns when done.
            await asyncio.gather(
                *[
                    self.com.send(x)
                    for x in (
                        ObjCmd.SWYZ,
                        ObjCmd.SET_VELO(0.42),
                        ObjCmd.SET_TRIGGER(z_max),
                        ObjCmd.ARM_TRIGGER,
                    )
                ]
            )
            yield self.com.send(ObjCmd.Z_MOVE(z_min))
        finally:
            await self.com.send(ObjCmd.SET_VELO(5))
