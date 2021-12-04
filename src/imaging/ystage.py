import logging
import time
from concurrent.futures import Future, ThreadPoolExecutor
from dataclasses import dataclass
from typing import Dict, Literal, Optional

from src.base.instruments import Movable, UsesSerial
from src.com.async_com import COM, CmdParse
from src.utils.utils import ok_if_match
from src.com.thread_mgt import run_in_executor

logger = logging.getLogger("YStage")


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
    "IMAGING": {"GAINS": "6,10,7,1.5,0", "VELO": "0.154"},
    "MOVING": {"GAINS": "7,10,7,1.5,0", "VELO": "1"},
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


def read_pos(resp: str) -> int:
    return int(resp[1:])


class YCmd:
    """
    See https://www.parkermotion.com/manuals/Digiplan/ViX-IH_UG_7-03.pdf for more.
    """

    SET_POS = lambda x: f"D{x}"
    GO = "G"
    STOP = "S"
    IS_MOVING = CmdParse("R(IP)", lambda x: not bool(read_pos(x)))  # Intentional inversion.
    READ_POS = CmdParse("R(PA)", read_pos)  # Report(Position Actual)
    TARGET_POS = CmdParse("R(PT)", read_pos)
    GAINS = lambda x: f"GAINS({x})"
    VELO = lambda x: f"V{x}"
    DONT_ECHO = "W(EX,0)"

    ON = "ON"
    GO_HOME = "GH"
    MODE_ABSOLUTE = "MA"  # p.159
    RESET = CmdParse(
        "Z",
        ok_if_match("*ViX250IH-Servo Drive\n*REV 2.4 Jun 29 2005 16:58:18\nCopyright 2003 Parker-Hannifin"),
        n_lines=3,
    )  # p.96, 180


class YStage(UsesSerial, Movable):
    HOME = 0
    RANGE = (int(-7e6), int(7.5e6))
    STEPS_PER_UM = 100

    cmd = YCmd

    def __init__(self, port_tx: str, tol: int = 10) -> None:
        self.com = COM("y", port_tx)

        self.__mode: Optional[ModeName] = None
        self.tol = tol
        self._executor = ThreadPoolExecutor(max_workers=1)

    @run_in_executor
    def initialize(self) -> None:
        logger.info("Initializing y-stage.")
        self.com.send(YCmd.RESET)  # Initialize Stage
        time.sleep(3)
        self.com.send(CmdParse(YCmd.DONT_ECHO, lambda x: x == "1W(EX,0)"))  # Turn off echo
        self.com.send("BRAKE0")
        self._mode = "MOVING"
        self.com.send(YCmd.GAINS(MODES["MOVING"]["GAINS"]))
        self.com.send(("MA", "ON"))
        return self.com.send("GH")

    def move(self, pos: int, slowly: bool = False):
        # TODO: Parse
        if not (self.RANGE[0] <= pos <= self.RANGE[1]):
            raise ValueError(f"YSTAGE can only be between {self.RANGE[0]} and {self.RANGE[1]}")
        self._mode = "IMAGING" if slowly else "MOVING"
        fut = self.com.send((YCmd.SET_POS(pos), YCmd.GO))
        logger.info(f"Moving to {pos} for {self._mode}")
        # def work() -> int:
        #     self.com.send(is_between(YCmd.SET_POS, *self.RANGE)(pos))  # type: ignore[operator]
        #     while abs((curr := self.position.result()) - pos) > self.tol:
        #         self.com.send(YCmd.GO)
        #         while not self.is_in_position:
        #             time.sleep(0.1)
        #     return curr

    @property
    def position(self) -> Future[Optional[int]]:
        return self.com.send(YCmd.READ_POS)

    @property
    def is_moving(self) -> Future[Optional[bool]]:
        return self.com.send(YCmd.IS_MOVING)

    @property
    def _mode(self) -> Optional[ModeName]:
        return self.__mode

    @_mode.setter
    def _mode(self, mode: ModeName) -> None:
        if self.__mode == mode:
            return
        self.com.send(YCmd.VELO(MODES[mode]["VELO"]))
        self.__mode = mode
