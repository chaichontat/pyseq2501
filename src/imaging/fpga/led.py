from enum import IntEnum, unique
from logging import getLogger
from typing import Literal

from src.base.instruments import FPGAControlled
from src.com.async_com import COM, CmdParse
from src.utils.utils import ok_if_match

logger = getLogger("LED")

ID = Literal[1, 2]


@unique
class LEDColor(IntEnum):
    OFF = 0
    YELLOW = 1
    GREEN = 3
    PULSE_GREEN = 4
    BLUE = 5
    PULSE_BLUE = 6
    SWEEP_BLUE = 7


class LEDCmd:
    SET_MODE = CmdParse(lambda i, x: f"LEDMODE{i} {x}", ok_if_match(["LEDMODE1", "LEDMODE2"]))
    SET_SWEEP_RATE = CmdParse(lambda x: f"LEDSWPRATE {x}", ok_if_match("LEDSWPRATE"))
    SET_PULSE_RATE = CmdParse(lambda x: f"LEDPULSRATE {x}", ok_if_match("LEDPULSRATE"))


class LED(FPGAControlled):
    colors = LEDColor
    cmd = LEDCmd

    def __init__(self, fpga_com: COM) -> None:
        super().__init__(fpga_com)
        self._color = [LEDColor.OFF, LEDColor.OFF]

    @property
    def color(self):
        return self._color
