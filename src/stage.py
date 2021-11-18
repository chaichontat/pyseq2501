import logging
import time
from typing import Dict, Literal, Optional

from com import COM, Command

logger = logging.getLogger(__name__)


MIN_Y = int(-7e6)
MAX_Y = int(7.5e6)
STEPS_PER_UM = 100
PREFIX = "1"
SUFFIX = "\r\n"
CONFIGS = {
    "imaging": {"g": "5,10,5,2,0", "v": 0.154},
    "moving": {"g": "5,10,7,1.5,0", "v": 1},
}


class YCommand(Command):
    SET_POS = staticmethod(lambda x: f"D{x}")
    GO = "G"
    CHECK_POS = "R(IP)"
    READ_POS = "R(PA)"
    GAINS = staticmethod(lambda x: f"GAINS({x})")
    VELO = staticmethod(lambda x: f"V{x}")


ModeParams = Literal["GAINS", "VELO"]
ModeName = Literal["IMAGING", "MOVING"]


MODES: Dict[ModeName, Dict[ModeParams, str]] = {
    "IMAGING": {"GAINS": "5,10,7,1.5,0", "VELO": "0.154"},
    "MOVING": {"GAINS": "5,10,7,1.5,0", "VELO": "1"},
}


class BetterYstage:
    def __init__(self, com_port: str) -> None:
        # super().__init__(com_port, baudrate=baudrate, logger=logger)
        self.__mode: Optional[ModeName] = None
        self.com = COM(com_port, 9600, logger, prefix="1", suffix="\r\n")
        self.send = self.com.send

    def initialize(self) -> None:
        self.send("Z")  # Initialize Stage
        time.sleep(2)
        self.send("W(EX,0)")  # Turn off echo
        self.mode = "MOVING"
        self.send("MA")  # Set to absolute position mode
        self.send("ON")  # Turn Motor ON
        self.send("GH")  # Home Stage

    @property
    def pos(self) -> int:
        return int(self.send(YCommand.READ_POS)[1:])

    @pos.setter
    def pos(self, pos: int) -> None:
        self.move(pos)

    @property
    def is_in_position(self) -> bool:
        return self.com.send(YCommand.CHECK_POS)[1:] == "1"

    @property
    def mode(self) -> Optional[ModeName]:
        return self.__mode

    @mode.setter
    def mode(self, mode: ModeName) -> bool:
        if self.__mode == mode:
            return True
        self.send(YCommand.GAINS(MODES[mode]["GAINS"]))  # type: ignore[operator]
        self.send(YCommand.VELO(MODES[mode]["VELO"]))  # type: ignore[operator]
        return True

    def move(self, pos: int, tol: int = 10) -> int:
        """Move ystage to absolute step position.

        **Parameters:**
         - position (int): Absolute step position must be between -7000000
           and 7500000.

        """
        if not (MIN_Y <= pos <= MAX_Y):
            raise ValueError(f"YSTAGE can only be between {MIN_Y} and {MAX_Y}")

        while abs(self.pos - pos) > tol:
            self.send(YCommand.SET_POS(pos))  # type: ignore[operator]
            self.send(YCommand.GO)
            while not self.is_in_position:
                time.sleep(1)
        return self.pos
