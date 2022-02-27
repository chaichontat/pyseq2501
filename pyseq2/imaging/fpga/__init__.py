from __future__ import annotations

import asyncio
from logging import getLogger
from typing import Awaitable

from .led import LED
from .optics import Optics
from .tdi import TDI
from .z_obj import ZObj
from .z_tilt import ZTilt
from pyseq2.base.instruments import UsesSerial
from pyseq2.com.async_com import COM, CmdParse
from pyseq2.utils.utils import ok_if_match

logger = getLogger(__name__)


class FPGACmd:
    RESET = CmdParse("RESET", ok_if_match("@LOG The FPGA is now online.  Enjoy!\nRESET"), n_lines=2)


class FPGA(UsesSerial):
    """Instruments controlled by the FPGA."""

    @classmethod
    async def ainit(cls, port_tx: str, port_rx: str) -> FPGA:
        self = cls()
        self.com = await COM.ainit("fpga", port_tx, port_rx)

        self.tdi = TDI(self.com)
        self.led = LED(self.com)
        self.optics = Optics(self.com)
        self.z_obj = ZObj(self.com)
        self.z_tilt = ZTilt(self.com)
        await self.reset()
        return self

    def __init__(self) -> None:
        self.com: COM
        self.tdi: TDI
        self.led: LED
        self.optics: Optics
        self.z_obj: ZObj
        self.z_tilt: ZTilt

    async def initialize(self) -> None:
        async with self.com.big_lock:
            await self.reset()
            await asyncio.sleep(1)  # Otherwise the FPGA hangs.

    async def initialize_all(self) -> None:
        await asyncio.gather(self.z_tilt.initialize(), self.z_obj.initialize(), self.optics.initialize())

    async def reset(self) -> bool:
        return await self.com.send(FPGACmd.RESET)
