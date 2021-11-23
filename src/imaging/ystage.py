from __future__ import annotations

import logging
import time
from concurrent.futures import Future
from contextlib import contextmanager
from typing import Dict, Iterator, Literal, Optional

from src.instruments import Movable, UsesSerial
from src.utils.com import COM, CmdVerify, is_between

logger = logging.getLogger(__name__)


ModeParams = Literal["GAINS", "VELO"]
ModeName = Literal["IMAGING", "MOVING"]


MODES: Dict[ModeName, Dict[ModeParams, str]] = {
    "IMAGING": {"GAINS": "5,10,7,1.5,0", "VELO": "0.154"},
    "MOVING": {"GAINS": "5,10,7,1.5,0", "VELO": "1"},
}


class YCmd:
    SET_POS = lambda x: f"D{x}"
    GO = "G"
    CHECK_POS = "R(IP)"
    READ_POS = "R(PA)"
    GAINS = lambda x: f"GAINS({x})"
    VELO = lambda x: f"V{x}"


# class YCommandVerify:
#     SET_POS = CmdVerify(YCmd.SET_POS, lambda ver, cmd: ver == cmd)
#     GO = CmdVerify()


class YStage(UsesSerial, Movable):
    HOME = 0
    RANGE = (int(-7e6), int(7.5e6))
    STEPS_PER_UM = 100

    def __init__(self, port_tx: str, tol: int = 10) -> None:
        self.com = COM("y", port_tx, logger=logger)

        self.__mode: Optional[ModeName] = None
        self.tol = tol

    def initialize(self) -> Future[None]:
        self.com.repl("Z")  # Initialize Stage
        self.com.put(lambda: time.sleep(2))
        self.com.repl("W(EX,0)")  # Turn off echo
        self._mode = "MOVING"
        [self.com.repl(x) for x in ["MA", "ON, GH"]]
        return self.com.is_done()
        # Set to absolute position mode
        # Turn Motor ON
        # Home Stage

    def move(self, pos: int) -> Future[int]:
        if not (self.RANGE[0] <= pos <= self.RANGE[1]):
            raise ValueError(f"YSTAGE can only be between {self.RANGE[0]} and {self.RANGE[1]}")

        def work() -> int:
            self.com.repl(is_between(YCmd.SET_POS, *self.RANGE)(pos))  # type: ignore[operator]
            while abs((curr := self.position.result()) - pos) > self.tol:
                self.com.repl(YCmd.GO)
                while not self.is_in_position:
                    time.sleep(0.1)
            return curr

        return self.com.put(work)

    @property
    def position(self) -> Future[int]:
        return self.com.put(lambda: int(self.com.repl(YCmd.READ_POS).result()[1:]))

    @property
    def is_in_position(self) -> Future[bool]:
        return self.com.put(lambda: self.com.repl(YCmd.CHECK_POS)[1:] == "1")

    @property
    def _mode(self) -> Optional[ModeName]:
        return self.__mode

    @_mode.setter
    def _mode(self, mode: ModeName) -> None:
        if self.__mode == mode:
            return
        self.com.repl(YCmd.GAINS(MODES[mode]["GAINS"]))  # type: ignore[operator]
        self.com.repl(YCmd.VELO(MODES[mode]["VELO"]))  # type: ignore[operator]

    @contextmanager
    def _imaging_mode(self) -> Iterator[None]:
        self._mode = "IMAGING"
        self.com.is_done().result()
        yield
        self._mode = "MOVING"

    def move_slowly(self, target: int) -> Future[int]:
        with self._imaging_mode():
            return self.move(target)
