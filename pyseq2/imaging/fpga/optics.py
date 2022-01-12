import asyncio
from contextlib import asynccontextmanager
from logging import getLogger
from typing import AsyncGenerator, Literal, Optional

from pyseq2.base.instruments import FPGAControlled
from pyseq2.com.async_com import CmdParse
from pyseq2.com.thread_mgt import run_in_executor
from pyseq2.utils.utils import ok_if_match

logger = getLogger(__name__)

ID = Literal[1, 2]

# Unchecked
OD_GREEN = {
    "OPEN": 143,
    "1.0": 107,
    "2.0": 71,
    "3.5": -107,
    "3.8": -71,
    "4.0": 36,
    "4.5": -36,
    "CLOSED": 0,
}
OD_RED = {
    "OPEN": 143,
    "0.2": -107,
    "0.5": -71,
    "0.6": -36,
    "1.0": 107,
    "2.4": 71,
    "4.0": 36,
    "CLOSED": 0,
}


# fmt: off
class OpticCmd:
    EM_FILTER_DEFAULT = CmdParse("EM2I", ok_if_match("EM2I"))
    EM_FILTER_OUT     = CmdParse("EM2O", ok_if_match("EM2O"))
    HOME_OD           = CmdParse(lambda i   : f"EX{i}HM",     ok_if_match(("EX1HM", "EX2HM")))
    SET_OD            = CmdParse(lambda x, i: f"EX{i}MV {x}", ok_if_match(("EX1MV", "EX2MV")))
    OPEN_SHUTTER      = CmdParse("SWLSRSHUT 1", ok_if_match("SWLSRSHUT"))
    CLOSE_SHUTTER     = CmdParse("SWLSRSHUT 0", ok_if_match("SWLSRSHUT"))
# fmt: on


class Optics(FPGAControlled):
    """
    No reason to change this.
    Always set to no OD filters and emission filter in.
    """

    cmd = OpticCmd

    async def initialize(self) -> None:
        await self.com.send(OpticCmd.EM_FILTER_DEFAULT)
        await asyncio.gather(self.com.send(OpticCmd.HOME_OD(1)), self.com.send(OpticCmd.HOME_OD(2)))
        await asyncio.gather(
            self.com.send(OpticCmd.SET_OD(OD_GREEN["OPEN"], 1)),
            self.com.send(OpticCmd.SET_OD(OD_RED["OPEN"], 2)),
        )

    @asynccontextmanager
    async def open_shutter(self) -> AsyncGenerator[None, None]:
        await self._open()
        logger.info("Shutter opened.")
        try:
            yield
        finally:
            await self._close()
            logger.info("Shutter closed.")

    async def _open(self) -> bool:
        return await self.com.send(OpticCmd.OPEN_SHUTTER)

    async def _close(self) -> bool:
        return await self.com.send(OpticCmd.CLOSE_SHUTTER)
