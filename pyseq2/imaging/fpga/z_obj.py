import asyncio
from contextlib import asynccontextmanager
from logging import getLogger
from typing import AsyncGenerator, Awaitable

from pyseq2.base.instruments import FPGAControlled, Movable
from pyseq2.com.async_com import COM, CmdParse
from pyseq2.utils.utils import chkrng, ok_if_match, ok_re, λ_float, λ_int

logger = getLogger(__name__)


Y_OFFSET = int(7e6)
RANGE = (0, 65535)


class ObjCmd:
    # fmt: off
    # Callable[[Annotated[int, "mm/s"]], str]
    GET_TARGET_POS = CmdParse(     "ZDACR"              , ok_re(r"^ZDACR (\d+)$", int))  # D A
    GET_POS        = CmdParse(     "ZADCR"              , ok_re(r"^ZADCR (\d+)$", int))  # A D

    SET_VELO = CmdParse(λ_float(lambda x: f"ZSTEP {int(1288471 * x)}"), ok_if_match("ZSTEP"))
    SET_POS  = CmdParse(chkrng(λ_int(lambda x: f"ZDACW {x}"), *RANGE), ok_if_match("ZDACW"))

    # Autofocus stuffs
    SET_TRIGGER = CmdParse(λ_int(lambda x: f"ZTRG {x}") , ok_if_match("ZTRG"))
    ARM_TRIGGER = CmdParse(                 "ZYT 0 3"   , ok_if_match("ZYT"))
    Z_MOVE      = CmdParse(λ_int(lambda x: f"ZMV {x}")  , ok_if_match("@LOG Trigger Camera\nZMV"), n_lines=2)
    SWYZ        = CmdParse(                 "SWYZ_POS 1", ok_if_match("SWYZ_POS"))
    # fmt: on

    @staticmethod
    def handle_fake(s: str) -> str:
        match s:
            case "ZDACR" | "ZADCR" as e:
                return e + " 0"
            case _:
                ...

        match s.split():
            case ["ZSTEP" as e, _] | ["ZDACW" as e, _] | ["ZTRG" as e, _] | ["SWYZ_POS" as e, _]:
                return e
            case ["ZYT" as e, _, _]:
                return e
            case ["ZMV", _]:
                return "@LOG Trigger Camera\nZMV"
            case _:
                return "what?"


class ZObj(FPGAControlled, Movable):
    STEPS_PER_UM = 262
    RANGE = (0, 65535)
    HOME = 65535

    cmd = ObjCmd

    def __init__(self, fpga_com: COM) -> None:
        super().__init__(fpga_com)
        self.lock = asyncio.Lock()

    async def initialize(self) -> bool | None:
        return await self.com.send(ObjCmd.SET_VELO(5))

    @property
    async def pos(self) -> int:
        async with self.lock:
            return await self.com.send(ObjCmd.GET_POS)

    async def _move(self, pos: int) -> None:
        await self.com.send(ObjCmd.SET_POS(int(pos)))

    async def move(self, pos: int) -> None:
        async with self.lock:
            await self._move(pos)

    @asynccontextmanager
    async def af_arm(
        self, z_min: int = 2621, z_max: int = 60292, speed: float = 0.42
    ) -> AsyncGenerator[Awaitable[None | bool], None]:
        async with self.lock:
            try:
                await self._move(z_max)  # Returns when done.
                await asyncio.gather(
                    *[
                        self.com.send(x)
                        for x in (
                            ObjCmd.SWYZ,
                            ObjCmd.SET_VELO(speed),
                            ObjCmd.SET_TRIGGER(z_max),
                            ObjCmd.ARM_TRIGGER,
                        )
                    ]
                )
                yield self.com.send(ObjCmd.Z_MOVE(z_min))
            finally:
                await self.com.send(ObjCmd.SET_VELO(5))
