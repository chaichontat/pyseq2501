import time
from concurrent.futures import Future
from logging import getLogger
from typing import Literal

from src.base.instruments import UsesSerial
from src.com.async_com import COM, CmdParse
from src.com.thread_mgt import run_in_executor
from src.utils.utils import ok_if_match

from .led import LED
from .objstage import ObjStage
from .optics import Optics
from .tdi import TDI
from .tiltstage import TiltStage

logger = getLogger("fpga")


class FPGACmd:
    RESET = CmdParse("RESET", ok_if_match("@LOG The FPGA is now online.  Enjoy!\nRESET"), n_lines=2)


class FPGA(UsesSerial):
    def __init__(self, port_tx: str, port_rx: str) -> None:
        self.com = COM("fpga", port_tx, port_rx, min_spacing=0.01)
        self.tdi = TDI(self.com)
        self.led = LED(self.com)
        self.optics = Optics(self.com)
        self.z_obj = ObjStage(self.com)
        self.z = TiltStage(self.com)

        # assert all([x.fcom is self.com for x in (self.tdi, self.led, self.optics, self.z)])  # type: ignore[attr-defined]

    def initialize(self) -> Future[bool]:
        return self.reset()

    @run_in_executor
    def reset(self) -> Literal[True]:
        self.com.send(FPGACmd.RESET).result()
        return True
