from __future__ import annotations

from concurrent.futures import Future, wait
from logging import getLogger
from typing import Literal, Optional, cast, get_args

from pyseq2.base.instruments import FPGAControlled, Movable
from pyseq2.com.async_com import CmdParse
from pyseq2.com.thread_mgt import run_in_executor
from pyseq2.utils.utils import chkrng, ok_re

logger = getLogger(__name__)

ID = Literal[1, 3, 2]
RANGE = (0, 25000)
import re


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

    @run_in_executor
    def initialize(self) -> None:
        # self.com.send("TDIZ_PI_STAGE")
        logger.info("Initializing z-tilt.")
        for i in get_args(ID):
            self.com.send(TiltCmd.SET_CURRENT(35, i))
            self.com.send(TiltCmd.SET_VELO(62500, i))

        futs = [self.com.send(TiltCmd.GO_HOME(i)) for i in get_args(ID)]
        wait(futs, 60)  # Returns when move is completed.

        futs = self.com.send(tuple(TiltCmd.CLEAR_REGISTER(i) for i in get_args(ID)))
        wait(futs, 60)  # type: ignore

        assert all(x > -5 for x in self.pos.result(60))
        logger.info("Completed z-tilt initialization.")

    @run_in_executor
    def move(self, pos: int) -> bool:
        futs = [self.com.send(TiltCmd.SET_POS(pos, i)) for i in get_args(ID)]
        wait(futs, 60)
        return True

    @property
    @run_in_executor
    def pos(self) -> tuple[int, int, int]:
        resp = cast(
            tuple[Future[Optional[int]]], self.com.send(tuple(TiltCmd.READ_POS(i) for i in get_args(ID)))
        )

        out = tuple(x.result(60) for x in resp)
        if not all(map(lambda x: x >= 0, out)):  # type: ignore
            raise Exception("Invalid Z position. Clear register first.")
        return cast(tuple[int, int, int], out)

    @property
    def is_moving(self) -> Future[Literal[False]]:
        return self.com._executor.submit(lambda: False)
        # return any(a != b for a, b in zip(self.pos.result(60), self.pos.result(60)))
