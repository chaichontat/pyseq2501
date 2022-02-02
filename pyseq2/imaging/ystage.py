from __future__ import annotations

import logging
from dataclasses import dataclass
from typing import Any, Callable, Literal, Optional

from pyseq2.base.instruments import Movable, UsesSerial
from pyseq2.com.async_com import COM, CmdParse
from pyseq2.utils.utils import chkrng, ok_if_match, ok_re, λ_float, λ_int

logger = logging.getLogger(__name__)


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
MODES: dict[ModeName, dict[ModeParams, Any]] = {
    "IMAGING": {"GAINS": "5,10,7,1.5,0", "VELO": 0.154},
    "MOVING": {"GAINS": "5,10,7,1.5,0", "VELO": 1.5},
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
    return ok_re(rf"1{s}\n1?\*([\d\+\-]+)", int)


def echo(s: str) -> CmdParse[Any, bool]:
    return CmdParse(s, ok_if_match(f"1{s}"))


class YCmd:
    """
    See https://www.parkermotion.com/manuals/Digiplan/ViX-IH_UG_7-03.pdf for more.
    """

    # fmt: off
    SET_POS    = CmdParse(λ_int(chkrng(lambda x: f"D{x}", *RANGE)), ok_re(r"1D\-?\d+"))
    GET_POS    = CmdParse("R(PA)",                    gen_reader(r"R\(PA\)"), n_lines=2)  # Report(Position Actual)
    IS_MOVING  = CmdParse("R(MV)", lambda x: bool(gen_reader(r"R\(MV\)")(x)), n_lines=2)
    MOVE_DONE  = CmdParse("GOTO(CHKMV)", ok_if_match("1GOTO(CHKMV)"), n_lines=1, delayed_parser=ok_if_match("Move Done"))  # Returns when move is completed.
    TARGET_POS = CmdParse("R(PT)",                    gen_reader(r"R\(PT\)")    , n_lines=2)
    GAINS      = CmdParse(lambda x: f"GAINS({x})", ok_re(r"GAINS\(([\d\.,]+)\)"))
    VELO       = CmdParse(λ_float(lambda x: f"V{x}")      , ok_re(r"V([\d\.]+)"))

    GO            = echo("G")
    STOP          = echo("S")
    ON            = echo("ON")
    GO_HOME       = echo("GH")
    MODE_ABSOLUTE = echo("MA")  # p.159
    BRAKE_OFF     = echo("BRAKE0")
    # fmt: on

    RESET = CmdParse(
        "Z", ok_re(r"1Z\n\*ViX250IH\-Servo Drive\n\*REV 2\..+\n\*Copyright 2003 Parker\-Hannifin"), n_lines=4
    )  # p.96, 180


class YStage(UsesSerial, Movable):
    HOME = 0
    RANGE = (int(-7e6), int(7.5e6))
    STEPS_PER_UM = 100

    cmd = YCmd

    @classmethod
    async def ainit(cls, port_tx: str) -> YStage:
        self = cls()
        self.com = await COM.ainit("y", port_tx, separator=b"\r\n", min_spacing=0.02)
        return self

    def __init__(self) -> None:
        self.com: COM
        self._mode: Optional[ModeName] = None

    async def initialize(self) -> bool:
        async with self.com.big_lock:
            logger.info("Initializing y-stage.")
            [
                await self.com.send(x)  # Wait until command returns before sending more.
                for x in (
                    YCmd.RESET,  # Initialize Stage, wait 1-2 seconds
                    # Continuous execution. Necessary for update while waiting for move to complete.
                    echo("W(CQ,0)"),
                    *tuple(map(echo, ("DECLARE(CHKMV)", "CHKMV:", "TR(MV,=,0)", '"Move Done"', "END"))),
                    YCmd.BRAKE_OFF,
                    YCmd.GAINS("5,10,7,1.5,0"),
                    YCmd.VELO(MODES["MOVING"]["VELO"]),  # Moving
                    YCmd.MODE_ABSOLUTE,
                    YCmd.ON,
                    YCmd.GO_HOME,
                    YCmd.MOVE_DONE,
                )
            ]
            logger.info("Completed y-stage initialization.")
            return True

    async def move(self, pos: int, slowly: bool = False) -> bool:
        async with self.com.big_lock:
            await self.set_mode("IMAGING") if slowly else await self.set_mode("MOVING")
            logger.info(f"Moving to {pos} for {self._mode}")
            await self.com.send(YCmd.SET_POS(pos))
            await self.com.send(YCmd.GO)
            return await self.com.send(YCmd.MOVE_DONE)

    @property
    async def pos(self) -> int:
        return await self.com.send(YCmd.GET_POS)

    @property
    async def is_moving(self) -> bool:
        return await self.com.send(YCmd.IS_MOVING)

    async def set_mode(self, mode: ModeName) -> None:
        if self._mode == mode:
            return
        await self.com.send(YCmd.VELO(MODES[mode]["VELO"]))
        self._mode = mode
