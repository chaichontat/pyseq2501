from concurrent.futures import Future
from contextlib import contextmanager
from logging import getLogger
from typing import Literal, Optional, get_args

from src.base.instruments import FPGAControlled
from src.com.async_com import CmdParse
from src.utils.utils import ok_if_match

logger = getLogger("optics")

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


class OpticCmd:
    EM_FILTER_DEFAULT = CmdParse("EM2I", ok_if_match("EM2I"))
    EM_FILTER_OUT = CmdParse("EM2O", ok_if_match("EM2O"))
    HOME_OD = CmdParse(lambda i: f"EX{i}HM", ok_if_match([f"EM{i}HM" for i in get_args(ID)]))
    SET_OD = CmdParse(lambda x, i: f"EX{i}MV {x}", ok_if_match([f"EM{i}MV" for i in get_args(ID)]))
    OPEN_SHUTTER = CmdParse("SWLSRSHUT 1", ok_if_match("SWLSRSHUT"))
    CLOSE_SHUTTER = CmdParse("SWLSRSHUT 0", ok_if_match("SWLSRSHUT"))


class Optics(FPGAControlled):
    """
    No reason to change this.
    """

    cmd = OpticCmd

    def initialize(self):
        self.com.send(OpticCmd.EM_FILTER_DEFAULT)
        self.com.send((OpticCmd.HOME_OD(1), OpticCmd.HOME_OD(2)))
        self.com.send((OpticCmd.SET_OD(OD_GREEN["OPEN"], 1), OpticCmd.SET_OD(OD_RED["OPEN"], 2)))

    @contextmanager
    def open_shutter(self):
        self._open().result(2)
        try:
            yield
        finally:
            self._close()

    def _open(self) -> Future[Optional[bool]]:
        return self.com.send(OpticCmd.OPEN_SHUTTER)

    def _close(self) -> Future[Optional[bool]]:
        return self.com.send(OpticCmd.CLOSE_SHUTTER)
