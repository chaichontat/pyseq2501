import logging
import re
import time
from concurrent.futures import Future
from dataclasses import dataclass
from typing import Any, Callable, Dict, Literal, Optional

from pyseq2.base.instruments import Movable, UsesSerial
from pyseq2.com.async_com import COM, CmdParse
from pyseq2.com.thread_mgt import run_in_executor
from pyseq2.utils.utils import chkrng, ok_if_match, ok_re

logger = logging.getLogger("YStage")


ModeParams = Literal["GAINS", "VELO"]
ModeName = Literal["IMAGING", "MOVING"]
RANGE = (int(-7e6), int(7.5e6))

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


def gen_reader(s: str) -> Callable[[str], int]:
    return ok_re(fr"1{s}\n\*([\d\+\-]+)", int)


def gen_repeat(cmd: str) -> CmdParse[bool, Any]:
    return CmdParse(cmd, ok_if_match("1" + cmd))


class YCmd:
    """
    See https://www.parkermotion.com/manuals/Digiplan/ViX-IH_UG_7-03.pdf for more.
    """

    # fmt: off
    SET_POS    = CmdParse(chkrng(lambda x: f"D{x}", *RANGE), ok_re(r"1D\-?\d+"))
    GET_POS    = CmdParse("R(PA)",                    gen_reader(r"R\(PA\)"), n_lines=2)  # Report(Position Actual)
    IS_MOVING  = CmdParse("R(MV)", lambda x: bool(gen_reader(r"R\(MV\)")(x)), n_lines=2)
    MOVE_DONE  = CmdParse("GOTO(CHKMV)", ok_if_match("1GOTO(CHKMV)\nMove Done"), n_lines=2)  # Returns when move is completed.
    TARGET_POS = CmdParse("R(PT)",                    gen_reader(r"R\(PT\)")    , n_lines=2)
    GAINS      = CmdParse(lambda x: f"GAINS({x})", ok_re(r"GAINS\(([\d\.,]+)\)"))
    VELO       = CmdParse(lambda x: f"V{x}"      , ok_re(r"V([\d\.]+)"))

    GO            = gen_repeat("G")
    STOP          = gen_repeat("S")
    ON            = gen_repeat("ON")
    GO_HOME       = gen_repeat("GH")
    MODE_ABSOLUTE = gen_repeat("MA")  # p.159
    BRAKE_OFF     = gen_repeat("BRAKE0")
    # fmt: on

    RESET = CmdParse(
        "Z", ok_re(r"1Z\n\*ViX250IH\-Servo Drive\n\*REV 2\..+\n\*Copyright 2003 Parker\-Hannifin"), n_lines=4
    )  # p.96, 180


class YStage(UsesSerial, Movable):
    HOME = 0
    RANGE = (int(-7e6), int(7.5e6))
    STEPS_PER_UM = 100

    cmd = YCmd

    def __init__(self, port_tx: str, tol: int = 10) -> None:
        self.com = COM("y", port_tx)
        self._mode: Optional[ModeName] = None
        self.tol = tol

    @run_in_executor
    def initialize(self) -> bool:
        def echo(s: str) -> CmdParse[bool, Any]:
            return CmdParse(s, ok_if_match(f"1{s}"))

        logger.info("Initializing y-stage.")
        self.com.send(YCmd.RESET).result(60)  # Initialize Stage, wait 1-2 seconds.
        self.com.send(echo("W(CQ,1)")).result()
        self.com.send(tuple(map(echo, ("DECLARE(CHKMV)", "CHKMV:", "TR(MV,=,0)", '"Move Done"', "END"))))
        self.com.send(YCmd.BRAKE_OFF).result(60)
        self.com.send(YCmd.GAINS("5,10,7,1.5,0")).result(60)
        self.set_mode("MOVING").result(60)
        self.com.send(YCmd.MODE_ABSOLUTE).result(60)
        self.com.send(YCmd.ON).result(60)
        self.com.send(YCmd.GO_HOME).result(60)
        self.com.send(YCmd.MOVE_DONE).result(60)
        logger.info("Completed y-stage initialization.")
        return True

    @run_in_executor
    def move(self, pos: int, slowly: bool = False) -> bool:
        self._mode = "IMAGING" if slowly else "MOVING"
        logger.info(f"Moving to {pos} for {self._mode}")
        self.com.send((YCmd.SET_POS(pos), YCmd.GO))
        return self.com.send(YCmd.MOVE_DONE).result(120)

    @property
    def pos(self) -> Future[int]:
        return self.com.send(YCmd.GET_POS)

    @property
    def is_moving(self) -> Future[bool]:
        return self.com.send(YCmd.IS_MOVING)

    @property
    def mode(self) -> Optional[ModeName]:
        return self._mode

    @mode.setter
    def mode(self, mode: ModeName) -> None:
        self.set_mode(mode)

    @run_in_executor
    def set_mode(self, mode: ModeName) -> bool:
        if self._mode == mode:
            return True
        fut = self.com.send(YCmd.VELO(MODES[mode]["VELO"]))
        self._mode = mode
        return fut.result()
