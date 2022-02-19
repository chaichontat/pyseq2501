import asyncio
from contextlib import asynccontextmanager
from logging import getLogger
from typing import AsyncGenerator, Literal

from pyseq2.base.instruments import FPGAControlled
from pyseq2.com.async_com import COM, CmdParse
from pyseq2.utils.utils import ok_if_match, λ_int

logger = getLogger(__name__)

# Open is 0. Closed is -1.
OD_GREEN = {
    "0.0": 143,
    "1.0": 107,
    "2.0": 71,
    "3.5": -107,
    "3.8": -71,
    "4.0": 36,
    "4.5": -36,
    "-1.0": 0,
}
OD_RED = {
    "0.0": 143,
    "0.2": -107,
    "0.5": -71,
    "0.6": -36,
    "1.0": 107,
    "2.4": 71,
    "4.0": 36,
    "-1.0": 0,
}


# fmt: off
class OpticCmd:
    EM_FILTER_DEFAULT = CmdParse("EM2I"       , None, ok_if_match("EM2I"))
    EM_FILTER_OUT     = CmdParse("EM2O"       , None, ok_if_match("EM2O"))
    OPEN_SHUTTER      = CmdParse("SWLSRSHUT 1", None, ok_if_match("SWLSRSHUT"))
    CLOSE_SHUTTER     = CmdParse("SWLSRSHUT 0", None, ok_if_match("SWLSRSHUT"))
    HOME_OD           = CmdParse(λ_int(lambda i   : f"EX{i}HM")    , None, ok_if_match(("EX1HM", "EX2HM")))
    SET_OD            = CmdParse(λ_int(lambda x, i: f"EX{i}MV {x}"), None, ok_if_match(("EX1MV", "EX2MV")))
# fmt: on


class Filter(FPGAControlled):
    def __init__(self, fpga_com: COM, id_: Literal[0, 1], lock: asyncio.Lock) -> None:
        super().__init__(fpga_com)
        self.lock = lock
        self.id_ = id_
        self.vals = OD_GREEN if id_ == 0 else OD_RED
        self._pos = 0.0

    @property
    async def pos(self) -> float:
        return self._pos

    async def initialize(self) -> None:
        await self.com.send(OpticCmd.HOME_OD(self.id_ + 1))
        await self.move(0)

    async def open(self) -> None:
        await self.move(0)

    async def close(self) -> None:
        await self.move(-1)

    async def move(self, od: int | float) -> None:
        async with self.lock:
            try:
                await self.com.send(OpticCmd.SET_OD(self.vals[f"{od:.1f}"], self.id_ + 1))
                self._pos = float(od)
            except KeyError:
                raise KeyError(f"Invalid OD. Only {list(self.vals.keys())} allowed.")


class Optics(FPGAControlled):
    """
    Set to no OD filters/closed and emission filter in.
    Same as ZTilt, cannot run new commands while previous ones are pending.
    """

    cmd = OpticCmd

    def __init__(self, fpga_com: COM) -> None:
        super().__init__(fpga_com)
        self.lock = asyncio.Lock()
        self.filters = [Filter(fpga_com, 0, self.lock), Filter(fpga_com, 1, self.lock)]
        self._shutter = False

    @property
    async def shutter(self) -> bool:
        return self._shutter

    def __getitem__(self, k: Literal[0, 1]) -> Filter:
        return self.filters[k]

    async def initialize(self) -> None:
        logger.info(f"Initializing optics.")
        await self.filters[0].initialize()
        await self.filters[1].initialize()
        await self._close()
        logger.info(f"Done initializing optics.")

    @asynccontextmanager
    async def open_shutter(self) -> AsyncGenerator[None, None]:
        await self._open()
        try:
            yield
        finally:
            await self._close()

    async def _open(self) -> None:
        await self.com.send(OpticCmd.OPEN_SHUTTER)
        self._shutter = True
        logger.info("Shutter opened.")

    async def _close(self) -> None:
        await self.com.send(OpticCmd.CLOSE_SHUTTER)
        self._shutter = False
        logger.info("Shutter closed.")
