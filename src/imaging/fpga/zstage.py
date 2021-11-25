from __future__ import annotations

from concurrent.futures import Future
from functools import partial
from logging import getLogger
from typing import Callable, Literal, cast, get_args

from src.instruments import FPGAControlled, Movable
from src.utils.com import CmdParse, is_between

logger = getLogger("z")

ID = Literal[1, 2, 3]
import re


# fmt: off
class ZCmd:
    GO_HOME  = CmdParse(lambda i:       f"T{i}HM",         lambda x: re.search(r"^@TILTPOS[123] \d+$", x))
    READ_POS = CmdParse(lambda i:       f"T{i}RD",         lambda x: re.search(r"^T[123]RD \d+$", x))
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
            self.fcom.repl(ZCmd.GO_HOME(i))
        for i in get_args(ID):
            self.fcom.repl(ZCmd.CLEAR_REGISTER(i))

    def move(self, pos: int) -> list[Future[str]]:
        return [self.fcom.repl(is_between(partial(ZCmd.SET_POS.cmd, i), *self.RANGE)(pos)) for i in get_args(ID)]  # type: ignore

    def position(self):
        ...
