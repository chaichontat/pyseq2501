from enum import IntEnum, unique
from logging import getLogger
from typing import Literal

from pyseq2.base.instruments import FPGAControlled
from pyseq2.com.async_com import CmdParse
from pyseq2.utils.utils import ok_if_match, λ_int

logger = getLogger(__name__)

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


# fmt: off
class LEDCmd:
    SET_MODE       = CmdParse(λ_int(lambda x, i: f"LEDMODE{i} {x}") , ok_if_match(["LEDMODE1", "LEDMODE2"]))
    SET_SWEEP_RATE = CmdParse(λ_int(lambda x:    f"LEDSWPRATE {x}") , ok_if_match("LEDSWPRATE"))
    SET_PULSE_RATE = CmdParse(λ_int(lambda x:    f"LEDPULSRATE {x}"), ok_if_match("LEDPULSRATE"))
# fmt:on


class LED(FPGAControlled):
    colors = LEDColor
    cmd = LEDCmd

    # def __init__(self, fpga_com: COM) -> None:
    #     super().__init__(fpga_com)
    #     self._color = [LEDColor.OFF, LEDColor.OFF]

    # @property
    # def color(self):
    #     return self._color
