from contextlib import contextmanager
from logging import getLogger
from typing import Literal, get_args

from src.instruments import FPGAControlled
from src.utils.com import CmdParse, ok_if_match

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
    SET_OD = CmdParse(lambda i, x: f"EX{i}MV {x}", ok_if_match([f"EM{i}MV" for i in get_args(ID)]))
    OPEN_SHUTTER = "SWLSRSHUT 1"
    CLOSE_SHUTTER = "SWLSRSHUT 0"


class Optics(FPGAControlled):
    """
    No reason to change this.
    """

    cmd = OpticCmd

    def initialize(self):
        self.fcom.repl(OpticCmd.EM_FILTER_DEFAULT)
        self.fcom.repl(OpticCmd.SET_OD(1, OD_GREEN["OPEN"]))
        self.fcom.repl(OpticCmd.SET_OD(2, OD_RED["OPEN"]))

    @contextmanager
    def open_shutter(self):
        self.fcom.repl(OpticCmd.OPEN_SHUTTER).result()
        try:
            yield
        finally:
            self.fcom.repl(OpticCmd.CLOSE_SHUTTER)
