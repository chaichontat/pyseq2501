from __future__ import annotations

import asyncio
import logging
from typing import Any

from pyseq2.base.instruments import Movable, UsesSerial
from pyseq2.com.async_com import COM, CmdParse
from pyseq2.utils.utils import chkrng, ok_if_match, ok_re

logger = logging.getLogger(__name__)
RANGE = (1000, 50000)


# fmt: off
class XCmd:
    """ See manual p. 61 for summary.
    `PR $VAR`   : Print selected data or text
    `$VAR=$VAL` : Set $VAR to $VAL
    """
    IS_MOVING   = CmdParse("PR MV", ok_re(fr"\??PR MV\n(\-?\d+)", lambda x: bool(int(x))), n_lines=2)
    GET_POS     = CmdParse("PR P" , ok_re(fr"\??PR P\n(\-?\d+)", int), n_lines=2)
    SET_POS     = CmdParse(chkrng(lambda x: f"MA {x},1", *RANGE), ok_re(r"\??MA (\d+),1"))  # Set mode and move to abs. position.
    SET_POS_REL = lambda x: f"MR {x}"  # Set mode and move to rel. position.
    RESET       = CmdParse("\x03", ok_re(r".*(Copyright© 2010 Schneider Electric Motion USA)|(Copyright© 2001-2009 by Intelligent Motion Systems, Inc.)"))
# fmt: on


class XStage(UsesSerial, Movable):
    HOME = 30000
    RANGE = (1000, 50000)
    STEPS_PER_UM = 0.4096

    cmd = XCmd

    @classmethod
    async def ainit(cls, port_tx: str) -> XStage:
        self = cls()
        self.com = await COM.ainit("x", port_tx, min_spacing=0.3)
        return self

    def __init__(self) -> None:
        self.com: COM

    @property
    async def pos(self) -> int:
        return await self.com.send(XCmd.GET_POS)

    @property
    async def is_moving(self) -> bool:
        return await self.com.send(XCmd.IS_MOVING)

    async def move(self, pos: int) -> bool:
        """Returns when move is completed."""
        return await self.com.send(XCmd.SET_POS(pos))

    async def initialize(self) -> bool:
        """Initialize the xstage."""
        logger.info("Initializing x-stage.")

        def echo(s: str) -> CmdParse[bool, Any]:
            return CmdParse(s, ok_if_match(f">{s}"))

        await self.com.send(XCmd.RESET)
        await asyncio.gather(
            (
                self.com.send(x)
                for x in (
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
                    # Program 1. Set Home to 30000.
                )
            )
        )

        for x in (
            echo("PG 1"),
            CmdParse("HM 1", ok_if_match("1  HM 1")),
            CmdParse("H", ok_if_match("5  H")),
            CmdParse("P=30000", ok_if_match("7  P=30000")),
            CmdParse("E", ok_if_match("12  E")),
            CmdParse("PG", ok_if_match("14  PG")),
        ):
            await self.com.send(x)

        await self.com.send(CmdParse("EX 1", ok_if_match(">EX 1\n>"), n_lines=2))
        logger.info("Completed x-stage initialization.")
        return True
