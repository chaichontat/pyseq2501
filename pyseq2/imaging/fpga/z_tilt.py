from __future__ import annotations

import asyncio
from logging import getLogger
from typing import Any, Callable, Iterable, Literal, TypeVar, cast

from pyseq2.base.instruments import FPGAControlled, Movable
from pyseq2.com.async_com import COM, CmdParse
from pyseq2.utils.log import init_log
from pyseq2.utils.utils import chkrng, ok_re, λ_int

logger = getLogger(__name__)
T = TypeVar("T")
ID = Literal[1, 3, 2]
RANGE = (0, 25000)


# fmt: off
class TiltCmd:
    READ_POS = CmdParse(λ_int(       lambda i   : f"T{i}RD")                 , ok_re(r"^T[123]RD (\-?\d+)$", int))
    GO_HOME  = CmdParse(λ_int(       lambda i   : f"T{i}HM")                 , None, ok_re(r"@TILTPOS[123] \-?\d+\nT[123]HM"), n_lines=2)
    CLEAR_REGISTER = CmdParse(λ_int( lambda i   : f"T{i}CR"),         ok_re(r"^T[123]CR$"))
    SET_POS  = CmdParse(λ_int(chkrng(lambda i, x: f"T{i}MOVETO {x}", *RANGE)), None, ok_re(r"^T[123]MOVETO \d+$"))
    SET_VELO =    CmdParse(λ_int(    lambda i, x: f"T{i}VL {x}"),     ok_re(r"^T[123]VL$"))
    SET_CURRENT = CmdParse(λ_int(    lambda i, x: f"T{i}CUR {x}"),    ok_re(r"^T[123]CUR$"))
# fmt:on


class ZTilt(FPGAControlled):
    STEPS_PER_UM = 0.656
    RANGE = (0, 25000)
    HOME = 21500

    cmd = TiltCmd

    """
    ZTilt cannot send commands while waiting for move.
    Otherwise get `^T2RD Command already in progress`.
    Commands for other FPGA instruments work fine.
    """

    def __init__(self, fpga_com: COM) -> None:
        super().__init__(fpga_com)
        self.lock = asyncio.Lock()

    async def all_z(self, cmd: Callable[[int], CmdParse[Any, T]]) -> tuple[T, T, T]:
        return await asyncio.gather(self.com.send(cmd(1)), self.com.send(cmd(3)), self.com.send(cmd(2)))

    async def _home(self) -> None:
        await self.all_z(TiltCmd.GO_HOME)
        await self.all_z(TiltCmd.CLEAR_REGISTER)

    @init_log(logger)
    async def initialize(self) -> None:
        async with self.lock:
            await asyncio.gather(
                self.all_z(lambda i: TiltCmd.SET_CURRENT(i, 35)),
                self.all_z(lambda i: TiltCmd.SET_VELO(i, 62500)),
            )
            await self._home()

    async def move(self, pos: int | tuple[int, int, int]) -> tuple[int, int, int]:
        async with self.lock:
            if isinstance(pos, Iterable):
                if len(pos) != 3:
                    raise ValueError("Need to specify all 3 Z tilt motors.")
                return cast(
                    tuple[int, int, int],
                    await asyncio.gather(
                        *[self.com.send(TiltCmd.SET_POS(i, p)) for i, p in enumerate(pos, 1)]
                    ),
                )
            return await self.all_z(lambda i: TiltCmd.SET_POS(i, int(pos)))

    @property
    async def pos(self) -> tuple[int, int, int]:
        async with self.lock:
            for i in range(1, 4):
                resp = await self.all_z(TiltCmd.READ_POS)
                if all(map(lambda x: x >= 0, resp)):
                    return resp
                logger.info(f"Negative Z position {resp}. Homing attempt {i}.")
                await self._home()

            raise Exception("Negative Z position after 3 homing attempts.")
