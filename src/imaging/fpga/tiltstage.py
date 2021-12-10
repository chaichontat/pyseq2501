from __future__ import annotations

from concurrent.futures import Future
from functools import partial
from logging import getLogger
from typing import Literal, Optional, cast, get_args

from src.base.instruments import FPGAControlled, Movable
from src.com.async_com import CmdParse
from src.utils.utils import not_none, chkrng
from src.com.thread_mgt import run_in_executor

logger = getLogger("z")

ID = Literal[1, 3, 2]
RANGE = (0, 25000)
import re


# fmt: off
class TiltCmd:
    GO_HOME  = CmdParse(lambda i:       f"T{i}HM",         lambda x: bool(re.search(r"^@TILTPOS[123] \d+$", x)))
    READ_POS = CmdParse(lambda i:       f"T{i}RD",         lambda x: int(not_none(re.search(r"^T[123]RD (\d+)$", x)).group(1)))
    SET_POS  = CmdParse(chkrng(lambda x, i: f"T{i}MOVETO {x}", *RANGE), lambda x: bool(re.search(r"^T[123]MOVETO \d+$", x)))
    CLEAR_REGISTER = CmdParse(lambda i: f"T{i}CR",         lambda x: bool(re.search(r"^T[123]CR$", x)))
    SET_VELO =    CmdParse(lambda x, i: f"T{i}VL {x}",     lambda x: bool(re.search(r"^T[123]VL$", x)))
    SET_CURRENT = CmdParse(lambda x, i: f"T{i}CUR {x}",    lambda x: bool(re.search(r"^T[123]CUR$", x)))
# fmt:on


class TiltStage(FPGAControlled, Movable):
    STEPS_PER_UM = 0.656
    RANGE = (0, 25000)
    HOME = 21500

    cmd = TiltCmd

    def initialize(self):
        self.com.send("TDIZ_PI_STAGE")
        for i in get_args(ID):
            self.com.send(TiltCmd.SET_CURRENT(35, i))
            self.com.send(TiltCmd.SET_VELO(62500, i))

        for i in get_args(ID):
            fut = self.com.send(tuple(TiltCmd.CLEAR_REGISTER(i) for i in get_args(ID)))
        [f.result(2) for f in fut]  # type: ignore

        for i in get_args(ID):
            self.com.send(TiltCmd.GO_HOME(i))

    def move(self, pos: int) -> list[Future[str]]:
        return [self.com.send(TiltCmd.SET_POS(pos, i)) for i in get_args(ID)]  # type: ignore

    @property
    @run_in_executor
    def position(self) -> tuple[int, int, int]:
        resp = cast(
            tuple[Future[Optional[int]]], self.com.send(tuple(TiltCmd.READ_POS(i) for i in get_args(ID)))
        )

        out = tuple(x.result(2) for x in resp)
        assert all(map(not_none, out))
        if not all(map(lambda x: x > 0, out)):  # type: ignore
            raise Exception("Invalid Z position. Clear register first.")
        return cast(tuple[int, int, int], out)

    @property
    @run_in_executor
    def is_moving(self) -> bool:
        return any(a != b for a, b in zip(self.position.result(2), self.position.result(2)))
