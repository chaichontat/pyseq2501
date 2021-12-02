from __future__ import annotations

from concurrent.futures import Future
from functools import partial
from logging import getLogger
from typing import Literal, cast, get_args

from src.base.instruments import FPGAControlled, Movable
from src.utils.async_com import COM, CmdParse
from src.utils.utils import run_in_executor, not_none

logger = getLogger("z")

ID = Literal[1, 3, 2]
import re


# fmt: off
class ZCmd:
    GO_HOME  = CmdParse(lambda i:       f"T{i}HM",         lambda x: re.search(r"^@TILTPOS[123] \d+$", x))
    READ_POS = CmdParse(lambda i:       f"T{i}RD",         lambda x: int(not_none(re.search(r"^T[123]RD (\d+)$", x)).group(1)))
    SET_POS  = CmdParse(lambda i, x:    f"T{i}MOVETO {x}", lambda x: re.search(r"^T[123]MOVETO \d+$", x))
    CLEAR_REGISTER = CmdParse(lambda i: f"T{i}CR",         lambda x: re.search(r"^T[123]CR$", x))
# fmt:on


class ZStage(FPGAControlled, Movable):
    STEPS_PER_UM = 0.656
    RANGE = (0, 25000)
    HOME = 21500

    cmd = ZCmd

    def initialize(self):
        for i in get_args(ID):
            self.com.send(ZCmd.GO_HOME(i))
        for i in get_args(ID):
            self.com.send(ZCmd.CLEAR_REGISTER(i))

    def move(self, pos: int) -> list[Future[str]]:
        return [self.com.send(is_between(partial(ZCmd.SET_POS.cmd, i), *self.RANGE)(pos)) for i in get_args(ID)]  # type: ignore

    @property
    @run_in_executor
    def position(self) -> tuple[int, int, int]:
        zs = tuple(self.com.send(ZCmd.READ_POS(i)) for i in get_args(ID))
        zs = tuple(x.result() for x in zs)
        return cast(tuple[int, int, int], zs)

    @property
    @run_in_executor
    def is_moving(self):
        return self.position.result() == self.position.result()
