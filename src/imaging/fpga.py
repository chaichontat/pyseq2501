import time
from concurrent.futures import Future
from enum import IntEnum, unique
from logging import getLogger
from typing import Callable, ClassVar

from src.utils.com import COM, Command

from .instruments import UsesSerial

logger = getLogger(__name__)


@unique
class LED_COLOR(IntEnum):
    OFF = 0
    YELLOW = 1
    GREEN = 3
    PULSE_GREEN = 4
    BLUE = 5
    PULSE_BLUE = 6
    SWEEP_BLUE = 7


Y_OFFSET = int(7e6)


class FPGACmds(Command):
    READ_Y = "TDIYERD"
    SET_Y = lambda x: f"TDIYPOS {x}"
    ARM = lambda n, y: f"TDIYARM3 {n} {y + Y_OFFSET - 10000} 1"


class FPGA(UsesSerial):
    BAUD_RATE = 115200
    COMMANDS = FPGACmds
    SERIAL_FORMATTER: ClassVar[Callable] = lambda _, x: f"{x}\n"

    def __init__(self, com_port_tx: str, com_port_rx: str) -> None:
        self.com = COM(
            self.BAUD_RATE, com_port_tx, com_port_rx, logger=logger, formatter=self.SERIAL_FORMATTER
        )

    def initialize(self) -> Future[str]:
        return self.com.repl("RESET")

    def read_position(self) -> Future[int]:
        """Read the y position of the encoder for TDI imaging.

        **Returns:**
         - int: The y position of the encoder.

        """
        return self.com.repl(FPGACmds.READ_Y).add_done_callback(
            lambda x: int(x.split(" ")[1][0:-1]) - Y_OFFSET
        )

        # tdi_pos = None
        # while not isinstance(tdi_pos, int):
        #     try:
        #         tdi_pos = self.command("TDIYERD")
        #         tdi_pos = tdi_pos.split(" ")[1]
        #         tdi_pos = int(tdi_pos[0:-1]) - self.y_offset
        #     except:
        #         tdi_pos = None
        # return tdi_pos

    def write_position(self, position):
        """Write the position of the y stage to the encoder.

        Allows for a 5 step (50 nm) error.

        **Parameters:**
         - position (int) = The position of the y stage.

        """
        position = position + self.y_offset
        while abs(self.read_position() + self.y_offset - position) > 5:
            self.command("TDIYEWR " + str(position))
            time.sleep(1)

    def TDIYPOS(self, y_pos) -> Future[str]:
        """Set the y position for TDI imaging.

        **Parameters:**
         - y_pos (int): The initial y position of the image.

        """
        return self.com.repl(FPGACmds.SET_Y(y_pos + Y_OFFSET - 80000))

    def TDIYARM3(self, n_triggers, y_pos) -> Future[str]:
        """Arm the y stage triggers for TDI imaging.

        **Parameters:**
         - n_triggers (int): Number of triggers to send to the cameras.
         - y_pos (int): The initial y position of the image.

        """
        return self.com.repl(FPGACmds.ARM(n_triggers, y_pos))

    def LED(self, AorB, mode, **kwargs):
        """Set front LEDs.

        **Parameters:**
         - AorB (int/str): A or 1 for the left LED, B or 2 for the right LED.
         - mode (str): Color / mode to set the LED to, see list below.
         - kwargs: sweep (1-255): sweep rate
                   pulse (1-255): pulse rate

        **Available Colors/Modes:**
         - off
         - yellow
         - green
         - pulse green
         - blue
         - pulse blue
         - sweep blue

        **Returns:**
         - bool: True if AorB and mode are valid, False if not.

        """

        s = None
        if type(AorB) is str:
            if AorB.upper() == "A":
                s = "1"
            elif AorB.upper() == "B":
                s = "2"
        elif type(AorB) is int:
            if AorB == 1 or AorB == 2:
                s = str(AorB)

        m = None
        if mode in self.led_dict:
            m = self.led_dict[mode]

        if s is not None and m is not None:
            response = self.command("LEDMODE" + s + " " + m)
            worked = True
        else:
            worked = False

        for key, value in kwargs.items():
            if 1 <= value <= 255:
                value = str(int(value))

                if key == "sweep":
                    response = self.command("LEDSWPRATE " + value)
                elif key == "pulse":
                    response = self.command("LEDPULSRATE " + value)

        return worked
