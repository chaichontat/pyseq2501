from __future__ import annotations

import asyncio
from logging import getLogger
from typing import Any, Awaitable, Callable, Literal, TypeVar, cast

from pyseq2.base.instruments import FPGAControlled, Movable
from pyseq2.com.async_com import CmdParse
from pyseq2.utils.utils import chkrng, ok_re

logger = getLogger(__name__)
T = TypeVar("T")
ID = Literal[1, 3, 2]
RANGE = (0, 25000)


# fmt: off
class TiltCmd:
    GO_HOME  = CmdParse(lambda i:       f"T{i}HM",         ok_re(r"@TILTPOS[123] \-?\d+\nT[123]HM"), n_lines=2)
    READ_POS = CmdParse(lambda i:       f"T{i}RD",         ok_re(r"^T[123]RD (\-?\d+)$", int))
    SET_POS  = CmdParse(chkrng(lambda x, i: f"T{i}MOVETO {x}", *RANGE), ok_re(r"^T[123]MOVETO \d+$"))
    CLEAR_REGISTER = CmdParse(lambda i: f"T{i}CR",         ok_re(r"^T[123]CR$"))
    SET_VELO =    CmdParse(lambda x, i: f"T{i}VL {x}",     ok_re(r"^T[123]VL$"))
    SET_CURRENT = CmdParse(lambda x, i: f"T{i}CUR {x}",    ok_re(r"^T[123]CUR$"))
# fmt:on


class ZTilt(FPGAControlled, Movable):
    STEPS_PER_UM = 0.656
    RANGE = (0, 25000)
    HOME = 21500

    cmd = TiltCmd

    def all_z(
        self, cmd: Callable[[int], CmdParse[T, Any]]
    ) -> tuple[Awaitable[T], Awaitable[T], Awaitable[T]]:
        return self.com.send(cmd(1)), self.com.send(cmd(3)), self.com.send(cmd(2))

    async def initialize(self) -> None:
        # self.com.send("TDIZ_PI_STAGE")
        logger.info("Initializing z-tilt.")
        await asyncio.gather(
            *self.all_z(lambda i: TiltCmd.SET_CURRENT(35, i)), *self.all_z(lambda i: TiltCmd.SET_VELO(35, i))
        )
        await asyncio.gather(*self.all_z(lambda i: TiltCmd.GO_HOME(i)))
        await asyncio.gather(*self.all_z(lambda i: TiltCmd.CLEAR_REGISTER(i)))
        assert all(x > -5 for x in await self.pos)
        logger.info("Completed z-tilt initialization.")

    async def move(self, pos: int) -> tuple[int, int, int]:
        return await cast(
            asyncio.Future[tuple[int, int, int]],
            asyncio.gather(*self.all_z(lambda i: TiltCmd.SET_POS(pos, i))),
        )

    @property
    async def pos(self) -> tuple[int, int, int]:
        resp = cast(tuple[int, int, int], await asyncio.gather(*self.all_z(lambda i: TiltCmd.READ_POS(i))))
        if not all(map(lambda x: x >= 0, resp)):
            raise Exception("Invalid Z position. Initialize first.")
        return resp
