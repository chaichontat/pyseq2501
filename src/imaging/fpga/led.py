from logging import getLogger

from src.instruments import UsesSerial
from src.utils.com import COM

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


class LED(FPGAControlled):
    ...


def led(self, AorB, mode, **kwargs):
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
