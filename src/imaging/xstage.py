import logging
from concurrent.futures import Future
from typing import Any

from src.base.instruments import Movable, UsesSerial
from src.com.async_com import COM, CmdParse
from src.com.thread_mgt import run_in_executor
from src.utils.utils import chkrng, ok_if_match, ok_re

logger = logging.getLogger("XStage")
RANGE = (1000, 50000)


# fmt: off
class XCmd:
    """ See manual p. 61 for summary.
    `PR $VAR`   : Print selected data or text
    `$VAR=$VAL` : Set $VAR to $VAL
    """
    IS_MOVING   = CmdParse("PR MV", ok_re(fr"\??PR MV\n(\-?\d+)", lambda x: bool(int(x))), n_lines=2)
    GET_POS     = CmdParse("PR P" , ok_re(fr"\??PR P\n(\-?\d+)", int), n_lines=2)
    SET_POS     = CmdParse(chkrng(lambda x: f"MA {x},1", *RANGE), ok_re(r"\??MA (\d+),1\n[\?>]!"), n_lines=2)  # Set mode and move to abs. position.
    SET_POS_REL = lambda x: f"MR {x}"  # Set mode and move to rel. position.
# fmt: on


class XStage(UsesSerial, Movable):
    HOME = 30000
    RANGE = (1000, 50000)
    STEPS_PER_UM = 0.4096

    cmd = XCmd

    def __init__(self, port_tx: str) -> None:
        self.com = COM("x", port_tx, min_spacing=0.3)

    @property
    def pos(self) -> Future[int]:
        return self.com.send(XCmd.GET_POS)

    @property
    def is_moving(self) -> Future[bool]:
        return self.com.send(XCmd.IS_MOVING)

    def move(self, pos: int) -> Future[int]:
        """Returns when move is completed."""
        return self.com.send(XCmd.SET_POS(pos))

    @run_in_executor
    def initialize(self) -> bool:
        """Initialize the xstage."""
        logger.info("Initializing x-stage.")

        def echo(s: str) -> CmdParse[bool, Any]:
            return CmdParse(s, ok_if_match(f">{s}"))

        self.com.send(
            CmdParse(
                "\x03",
                ok_re(
                    r".*(Copyright© 2010 Schneider Electric Motion USA)|(Copyright© 2001-2009 by Intelligent Motion Systems, Inc.)"
                ),
            )
        ).result(60)
        self.com.send(
            (
                echo("EM=0"),
                echo("EE=1"),
                echo("VI=640"),
                echo("VM=6144"),
                echo("A=4000"),
                echo("D=4000"),
                echo("S1=1,0,0"),
                echo("S2=3,1,0"),
                echo("S3=2,1,0"),
                echo("SM=0"),
                echo("LM=1"),
                echo("DB=8"),
                echo("D1=5"),
                echo("HC=20"),
                echo("RC=100"),
                echo("PG 1"),
                CmdParse("HM 1", ok_if_match("1  HM 1")),
                CmdParse("H", ok_if_match("5  H")),
                CmdParse("P=30000", ok_if_match("7  P=30000")),
                CmdParse("E", ok_if_match("12  E")),
                CmdParse("PG", ok_if_match("14  PG")),
            )
        )
        self.com.send(CmdParse("EX 1", ok_if_match(">EX 1\n>"), n_lines=2)).result(60)
        logger.info("Completed x-stage initialization.")
        return True
