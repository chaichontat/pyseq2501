from concurrent.futures import Future
from logging import getLogger

from src.base.instruments import UsesSerial
from src.utils.async_com import COM, CmdParse
from src.utils.utils import ok_if_match

from .led import LED
from .optics import Optics
from .tdi import TDI
from .zstage import ZStage

logger = getLogger("fpga")


class FPGACmd:
    RESET = CmdParse("RESET", ok_if_match("@LOG The FPGA is now online.  Enjoy!\nRESET"), n_lines=2)


class FPGA(UsesSerial):
    def __init__(self, port_tx: str, port_rx: str) -> None:
        self.com = COM("fpga", port_tx, port_rx, min_spacing=0)
        self.tdi = TDI(self.com)
        self.led = LED(self.com)
        self.optics = Optics(self.com)
        self.z = ZStage(self.com)

        # assert all([x.fcom is self.com for x in (self.tdi, self.led, self.optics, self.z)])  # type: ignore[attr-defined]

    def initialize(self) -> Future[None | bool]:
        return self.com.send(FPGACmd.RESET)
