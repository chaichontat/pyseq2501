import logging
from concurrent.futures import Future

from src.instruments import Movable, UsesSerial
from src.utils.com import COM, CmdParse

logger = logging.getLogger(__name__)

# fmt: off
class XCmd:
    """ See manual p. 61 for summary.
    `PR $VAR`   : Print selected data or text
    `$VAR=$VAL` : Set $VAR to $VAL
    """
    INIT = "\x03"
    IS_MOVING = CmdParse("PR MV", int)
    GET_POS   = CmdParse("PR P", int)
    SET_POS       = lambda x: f"MA {x}"  # Set mode and move to abs. position.
    SET_POS_REL   = lambda x: f"MR {x}"  # Set mode and move to rel. position.
# fmt: on


class XStage(UsesSerial, Movable):
    HOME = 30000
    RANGE = (1000, 50000)
    STEPS_PER_UM = 0.4096

    cmd = XCmd

    def __init__(self, port_tx: str) -> None:
        self.com = COM("x", port_tx, logger=logger)

    @property
    def position(self) -> Future:
        ...

    def initialize(self):
        """Initialize the xstage."""

        # Initialize Stage
        response = self.com.repl("\x03")

        # Change echo mode to respond only to print and list
        response = self.com.repl("EM=2")
        # Enable Encoder
        response = self.com.repl("EE=1")
        # Set Initial Velocity
        response = self.com.repl("VI=410")  # From Illumina log Ln 5247
        # Set Max Velocity
        response = self.com.repl("VM=6144")  # From Illumina log Ln 5243
        # Set Acceleration
        response = self.com.repl("A=4000")
        # Set Deceleration
        response = self.com.repl("D=4000")
        # Set Home
        response = self.com.repl("S1=1,0,0")
        # Set Neg. Limit
        response = self.com.repl("S2=3,1,0")
        # Set Pos. Limit
        response = self.com.repl("S3=2,1,0")
        # Set Stall Mode = stop motor
        response = self.com.repl("SM=0")
        # limit mode = stop if sensed
        response = self.com.repl("LM=1")
        # Encoder Deadband
        response = self.com.repl("DB=8")
        # Debounce home
        response = self.com.repl("D1=5")
        # Set hold current
        response = self.com.repl("HC=20")
        # Set run current
        response = self.com.repl("RC=100")

        # Home stage program
        self.com.send("PG 1")
        self.com.send("HM 1")
        self.com.send("H")
        self.com.send("P = 30000")
        self.com.send("E")
        self.com.send("PG")
        self.com._serial.flush()

        # Check if stage is homed correctly
        self.com.repl("EX 1")  # Execute home stage program
