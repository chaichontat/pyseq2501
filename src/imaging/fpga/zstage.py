from __future__ import annotations

from concurrent.futures import Future
from functools import partial
from logging import getLogger
from typing import Callable, Literal

from src.imaging import LOOP
from src.instruments import FPGAControlled, Movable
from src.utils.com import is_between

logger = getLogger("z")

ID = Literal[1, 2, 3]


class ZCmd:
    SET_POS: Callable[[ID, int], str] = lambda i, x: f"T{i}MOVETO {x}"
    GO_HOME: Callable[[ID], str] = lambda i: f"T{i}HM"
    READ_POS: Callable[[ID], str] = lambda i: f"T{i}RD"
    CLEAR_REGISTER: Callable[[ID], str] = lambda i: f"T{i}CR"


class ZStage(FPGAControlled, Movable):
    STEPS_PER_UM = 0.656
    RANGE = (0, 25000)
    HOME = 21500

    def move(self, pos: int) -> list[Future[str]]:
        return [
            self.fcom.repl(is_between(partial(ZCmds.SET_POS, i), *self.RANGE)(pos))  # type:ignore
            for i in range(1, 4)
        ]

    def position(self):
        ...
