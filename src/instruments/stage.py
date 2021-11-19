import logging
import time
from contextlib import contextmanager
from typing import Dict, Iterator, Literal, Optional

from com import COM, Command

logger = logging.getLogger(__name__)


ModeParams = Literal["GAINS", "VELO"]
ModeName = Literal["IMAGING", "MOVING"]


MODES: Dict[ModeName, Dict[ModeParams, str]] = {
    "IMAGING": {"GAINS": "5,10,7,1.5,0", "VELO": "0.154"},
    "MOVING": {"GAINS": "5,10,7,1.5,0", "VELO": "1"},
}


class YCommand(Command):
    SET_POS = staticmethod(lambda x: f"D{x}")
    GO = "G"
    CHECK_POS = "R(IP)"
    READ_POS = "R(PA)"
    GAINS = staticmethod(lambda x: f"GAINS({x})")
    VELO = staticmethod(lambda x: f"V{x}")


class BetterYstage:
    MIN_Y = int(-7e6)
    MAX_Y = int(7.5e6)
    STEPS_PER_UM = 100
    PREFIX = "1"
    SUFFIX = "\r\n"

    def __init__(self, com_port: str, tolerance: int = 10) -> None:
        self.com = COM(9600, com_port, logger=logger, prefix="1", suffix="\r\n")
        self.send = self.com.send

        self.__mode: Optional[ModeName] = None
        self.tolerance = tolerance

    def initialize(self) -> None:
        self.send("Z")  # Initialize Stage
        time.sleep(2)
        self.send("W(EX,0)")  # Turn off echo
        self._mode = "MOVING"
        self.send("MA")  # Set to absolute position mode
        self.send("ON")  # Turn Motor ON
        self.send("GH")  # Home Stage

    @property
    def position(self) -> int:
        return int(self.send(YCommand.READ_POS)[1:])

    @position.setter
    def position(self, pos: int) -> None:
        if not (self.MIN_Y <= pos <= self.MAX_Y):
            raise ValueError(f"YSTAGE can only be between {self.MIN_Y} and {self.MAX_Y}")

        while abs(self.position - pos) > self.tolerance:
            self.send(YCommand.SET_POS(pos))  # type: ignore[operator]
            self.send(YCommand.GO)
            while not self.is_in_position:
                time.sleep(0.1)

    @property
    def is_in_position(self) -> bool:
        return self.com.send(YCommand.CHECK_POS)[1:] == "1"

    @property
    def _mode(self) -> Optional[ModeName]:
        return self.__mode

    @_mode.setter
    def _mode(self, mode: ModeName) -> bool:
        if self.__mode == mode:
            return True
        self.send(YCommand.GAINS(MODES[mode]["GAINS"]))  # type: ignore[operator]
        self.send(YCommand.VELO(MODES[mode]["VELO"]))  # type: ignore[operator]
        return True

    @contextmanager
    def _imaging_mode(self) -> Iterator[None]:
        self._mode = "IMAGING"
        yield
        self._mode = "MOVING"

    def move_slowly(self, target: int) -> None:
        with self._imaging_mode():
            self.position = target
