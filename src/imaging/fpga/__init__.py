from concurrent.futures import Future
from logging import getLogger
from typing import Any

from src.instruments import UsesSerial
from src.utils.com import COM

from .led import LED
from .optics import Optics
from .tdi import TDI
from .zstage import ZStage

logger = getLogger(__name__)


class FPGACmd:
    RESET = "RESET"


class FPGA(UsesSerial):
    def __init__(self, port_tx: str, port_rx: str) -> None:
        self.com = COM(port_tx, port_rx, logger=logger)

        self.tdi = TDI(self.com)
        self.led = LED(self.com)
        self.optics = Optics(self.com)
        self.z = ZStage(self.com)

        assert all([x.fcom is self.com for x in (self.tdi, self.led, self.optics, self.z)])  # type: ignore[attr-defined]

    def initialize(self) -> Future[str]:
        return self.com.repl(FPGACmd.RESET)
