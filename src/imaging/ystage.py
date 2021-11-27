import logging
import time
from collections import namedtuple
from concurrent.futures import Future
from dataclasses import dataclass
from typing import Dict, Literal, Optional

from src.instruments import Movable, UsesSerial
from src.utils.com import COM, CmdParse

logger = logging.getLogger(__name__)


ModeParams = Literal["GAINS", "VELO"]
ModeName = Literal["IMAGING", "MOVING"]


"""
SCALE '*ON/OFF 0 SCLA 1 SCLD 42000 SCLV 1 PEU 42000' p.171

Somehow this is moving at 1.3e6 units/s
From the STATUS cmd => RESOLUTION ..........1300000
Also tested from moving, pinging and linear regression.

Imaging velo == 200200 units/s.

"""
MODES: Dict[ModeName, Dict[ModeParams, str]] = {
    "IMAGING": {"GAINS": "5,10,7,1.5,0", "VELO": "0.154"},
    "MOVING": {"GAINS": "5,10,7,1.5,0", "VELO": "1"},
}


@dataclass
class Gains:
    """
    GAINS(GF,GI,GP,GV,FT)
    GP : Gain Proportional
    GV : Gain Velocity feedback
    GF : Gain Feedforward
    GI : Gain Integral action
    FT : Filter time constant
    """

    GP: int
    GI: int
    GV: float
    GF: int

    def __str__(self) -> str:
        return f"GAINS({self.GF},{self.GI},{self.GP},{self.GV},0)"


{"SCANNING": Gains(GP=6, GI=10, GV=1.5, GF=5), "FASTMOVE": Gains(GP=7, GI=10, GV=1.5, GF=5)}


class YCmd:
    """
    See https://www.parkermotion.com/manuals/Digiplan/ViX-IH_UG_7-03.pdf for more.
    """

    @staticmethod
    def read_pos(resp: str) -> int:
        return int(resp[2:])

    SET_POS = lambda x: f"D{x}"
    GO = "G"
    STOP = "S"
    CHECK_POS = CmdParse("R(IP)", lambda x: bool(int(x[1:])))
    READ_POS = CmdParse("R(PA)", read_pos)  # Report(Position Actual)
    TARGET_POS = CmdParse("R(PT)", read_pos)
    GAINS = lambda x: f"GAINS({x})"
    VELO = lambda x: f"V{x}"
    DONT_ECHO = "W(EX,0)"

    ON = "ON"
    GO_HOME = "GH"
    MODE_ABSOLUTE = "MA"  # p.159
    RESET = CmdParse("Z", lambda x: x == "1Z")  # p.96, 180


class YStage(UsesSerial, Movable):
    HOME = 0
    RANGE = (int(-7e6), int(7.5e6))
    STEPS_PER_UM = 100

    cmd = YCmd

    # TODO: Daemon parameter checks

    def __init__(self, port_tx: str, tol: int = 10) -> None:
        self.com = COM("y", port_tx, logger=logger)

        self.__mode: Optional[ModeName] = None
        self.tol = tol

    def initialize(self) -> Future[None]:
        self.com.repl(YCmd.RESET)  # Initialize Stage
        self.com.put(lambda: time.sleep(2))
        self.com.repl("W(EX,0)")  # Turn off echo
        self._mode = "MOVING"
        self.com.send(["MA", "ON", "GH"])
        self.com.repl(YCmd.GAINS(MODES["MOVING"]["GAINS"]))
        return self.com.is_done()

    def move(self, pos: int, slowly: bool = False) -> Future[str]:
        # TODO: Parse
        if not (self.RANGE[0] <= pos <= self.RANGE[1]):
            raise ValueError(f"YSTAGE can only be between {self.RANGE[0]} and {self.RANGE[1]}")
        self._mode = "IMAGING" if slowly else "MOVING"

        # def work() -> int:
        #     self.com.repl(is_between(YCmd.SET_POS, *self.RANGE)(pos))  # type: ignore[operator]
        #     while abs((curr := self.position.result()) - pos) > self.tol:
        #         self.com.repl(YCmd.GO)
        #         while not self.is_in_position:
        #             time.sleep(0.1)
        #     return curr

        return self.com.repl(YCmd.SET_POS(pos))

    @property
    def position(self) -> Future[int]:
        return self.com.repl(YCmd.READ_POS)

    @property
    def is_in_position(self) -> Future[bool]:
        return self.com.repl(YCmd.CHECK_POS)

    @property
    def _mode(self) -> Optional[ModeName]:
        return self.__mode

    @_mode.setter
    def _mode(self, mode: ModeName) -> None:
        if self.__mode == mode:
            return
        self.com.repl(YCmd.VELO(MODES[mode]["VELO"]))  # type: ignore[operator]
