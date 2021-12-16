import time
from concurrent.futures import Future
from logging import getLogger

from src.base.instruments import UsesSerial
from src.com.async_com import COM, CmdParse
from src.com.thread_mgt import run_in_executor
from src.utils.utils import ok_if_match

from .led import LED
from .optics import Optics
from .tdi import TDI
from .z_obj import ZObj
from .z_tilt import ZTilt

logger = getLogger("fpga")


class FPGACmd:
    RESET = CmdParse("RESET", ok_if_match("@LOG The FPGA is now online.  Enjoy!\nRESET"), n_lines=2)


class FPGA(UsesSerial):
    def __init__(self, port_tx: str, port_rx: str) -> None:
        self.com = COM("fpga", port_tx, port_rx, min_spacing=0.01)
        self.tdi = TDI(self.com)
        self.led = LED(self.com)
        self.optics = Optics(self.com)
        self.z_obj = ZObj(self.com)
        self.z_tilt = ZTilt(self.com)
        self.initialize()

    @run_in_executor
    def initialize(self) -> bool:
        res = self.reset().result()
        time.sleep(1)  # Otherwise the FPGA hangs.
        return res

    def reset(self) -> Future[bool]:
        return self.com.send(FPGACmd.RESET)
