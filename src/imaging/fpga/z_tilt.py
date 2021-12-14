from __future__ import annotations

import time
from concurrent.futures import Future
from logging import getLogger
from typing import Literal, Optional, cast, get_args

from src.base.instruments import FPGAControlled, Movable
from src.com.async_com import CmdParse
from src.com.thread_mgt import run_in_executor
from src.utils.utils import chkrng, not_none, ok_re

logger = getLogger("z")

ID = Literal[1, 3, 2]
RANGE = (0, 25000)
import re


# fmt: off
class TiltCmd:
    GO_HOME  = CmdParse(lambda i:       f"T{i}HM",         ok_re(r"^@TILTPOS[123] \-?\d+$"))
    READ_POS = CmdParse(lambda i:       f"T{i}RD",         ok_re(r"^T[123]RD \-?(\d+)$", int))
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
        self.com.send("TDIZ_PI_STAGE")
        for i in get_args(ID):
            self.com.send(TiltCmd.SET_CURRENT(35, i))
            self.com.send(TiltCmd.SET_VELO(62500, i))

        for i in get_args(ID):
            self.com.send(TiltCmd.GO_HOME(i))

        time.sleep(8)  # Need a reliable way to check when move is complete.

        for i in get_args(ID):
            fut = self.com.send(tuple(TiltCmd.CLEAR_REGISTER(i) for i in get_args(ID)))

        # TODO: Verify if register is really cleared.
        [f.result(60) for f in fut]  # type: ignore

    def move(self, pos: int) -> list[Future[bool]]:
        return [self.com.send(TiltCmd.SET_POS(pos, i)) for i in get_args(ID)]  # type: ignore

    @property
    @run_in_executor
    def position(self) -> tuple[int, int, int]:
        resp = cast(
            tuple[Future[Optional[int]]], self.com.send(tuple(TiltCmd.READ_POS(i) for i in get_args(ID)))
        )

        out = tuple(x.result(60) for x in resp)
        assert all(map(not_none, out))
        if not all(map(lambda x: x > 0, out)):  # type: ignore
            raise Exception("Invalid Z position. Clear register first.")
        return cast(tuple[int, int, int], out)

    @property
    @run_in_executor
    def is_moving(self) -> bool:
        return any(a != b for a, b in zip(self.position.result(60), self.position.result(60)))
