import logging
from concurrent.futures import Future

from src.base.instruments import Movable, UsesSerial
from src.com.async_com import COM, CmdParse
from src.utils.utils import chkrng, ok_if_match, ok_re

logger = logging.getLogger("XStage")
RANGE = (1000, 50000)


# fmt: off
class XCmd:
    """ See manual p. 61 for summary.
    `PR $VAR`   : Print selected data or text
    `$VAR=$VAL` : Set $VAR to $VAL
    """
    INIT = "\x03"
    IS_MOVING   = CmdParse("PR MV", ok_re(fr"\??PR MV\n(\-?\d+)", lambda x: bool(int(x))), n_lines=2)
    GET_POS     = CmdParse("PR P" , ok_re(fr"\??PR P\n(\-?\d+)", int), n_lines=2)
    SET_POS     = CmdParse(chkrng(lambda x: f"MA {x}", *RANGE), ok_re(r"\?MA (\-?\d+)"))  # Set mode and move to abs. position.
    SET_POS_REL = lambda x: f"MR {x}"  # Set mode and move to rel. position.
# fmt: on


class XStage(UsesSerial, Movable):
    HOME = 30000
    RANGE = (1000, 50000)
    STEPS_PER_UM = 0.4096

    cmd = XCmd

    def __init__(self, port_tx: str) -> None:
        self.com = COM("x", port_tx, min_spacing=0.3)

    @property
    def position(self) -> Future[int]:
        return self.com.send(XCmd.GET_POS)

    @property
    def is_moving(self) -> Future[bool]:
        return self.com.send(XCmd.IS_MOVING)

    def move(self, pos: int) -> Future[bool]:
        return self.com.send(XCmd.SET_POS(pos))

    def initialize(self):
        """Initialize the xstage."""
        logger.info("Initializing x-stage.")
        self.com.send(CmdParse("\x03", ok_if_match("Copyright© 2010 Schneider Electric Motion USA")))
        self.com.send(
            (
                "EM=2",
                "EE=1",
                "VI=640",
                "VM=6144",
                "A=4000",
                "D=4000",
                "S1=1,0,0",
                "S2=3,1,0",
                "S3=2,1,0",
                "SM=0",
                "LM=1",
                "DB=8",
                "D1=5",
                "HC=20",
                "RC=100",
                "PG 1",
                "HM 1",
                "H",
                "P=30000",
                "E",
                "PG",
                "EX 1",
            )
        )

        "PR I1"

        def echo(s: str) -> bool:
            return self.com.send(CmdParse(s, ok_if_match(s))).result()

        # list(
        #     map(
        #         echo,
        #         (
        #             "FD",
        #             "L",
        #             "EE=1",
        #             "VI=1",
        #             "A=10000",
        #             "PG 1",
        #             "LB G2",
        #             "PM = 0",
        #             'PR "C1 ", C1',
        #             'PR "C2 ", C2',
        #             "H 50",
        #             "HM 1",
        #             "H",
        #             'PR "Homed at ", P',
        #             "P = 0",
        #             'PR "Homed OK"',
        #             "E",
        #             "PG",
        #             "L",
        #             "EE = 1",
        #             "VI = 1",
        #             "VM = 30720",
        #             "VI = 40",
        #             "A = 40000",
        #             "D = A",
        #             "HC = 20",
        #             "RC = 100",
        #             "MT = 100",
        #             "SM = 0",
        #             "SF = 15",
        #             "DB = 8",
        #             "LM = 1",
        #             "S1 = 1,0,0",
        #             "S2 = 3,1,0",
        #             "S3 = 2,1,0",
        #             "S4 = 0,0,0",
        #             "D1 = 5",
        #             "PR PN",
        #             "PR VR",
        #             "VI=1",
        #             "PR VI",
        #             "VM=6144",
        #             "PR VM",
        #             "VI=410",
        #             "PR VI",
        #             "A=16384",
        #             "D=A",
        #             "SF=8192",
        #             "P=0",
        #             "DE=1",
        #             "PR VM",
        #             "PR VI",
        #             "MA 0",
        #         ),
        #     )
        # )

        # (
        #     CmdParse("\x03", ok_if_match("Copyright© 2010 Schneider Electric Motion USA")),
        #     CmdParse("FD", ok_if_match("Copyright© 2010 Schneider Electric Motion USA")),
        #     CmdParse("\x03", ok_if_match("Copyright© 2010 Schneider Electric Motion USA")),
        #     CmdParse("\x03", ok_if_match("Copyright© 2010 Schneider Electric Motion USA")),
        # )
        # # Initialize Stage
        # return self.com.send(
        #     (
        #         "\x03",
        #         "EM=2",
        #         "EE=1",
        #         "VI=640",
        #         "VM=6144",
        #         "A=4000",
        #         "D=4000",
        #         "S1=1,0,0",
        #         "S2=3,1,0",
        #         "S3=2,1,0",
        #         "SM=0",
        #         "LM=1",
        #         "DB=8",
        #         "D1=5",
        #         "HC=20",
        #         "RC=100",
        #         "PG 1",
        #         "HM 1",
        #         "H",
        #         "P=30000",
        #         "E",
        #         "PG",
        #     )
        # )

        # # Change echo mode to respond only to print and list
        # response = self.com.send("EM=2")
        # # Enable Encoder
        # response = self.com.send("EE=1")
        # # Set Initial Velocity
        # response = self.com.send("VI=410")  # From Illumina log Ln 5247
        # # Set Max Velocity
        # response = self.com.send("VM=6144")  # From Illumina log Ln 5243
        # # Set Acceleration
        # response = self.com.send("A=4000")
        # # Set Deceleration
        # response = self.com.send("D=4000")
        # # Set Home
        # response = self.com.send("S1=1,0,0")
        # # Set Neg. Limit
        # response = self.com.send("S2=3,1,0")
        # # Set Pos. Limit
        # response = self.com.send("S3=2,1,0")
        # # Set Stall Mode = stop motor
        # response = self.com.send("SM=0")
        # # limit mode = stop if sensed
        # response = self.com.send("LM=1")
        # # Encoder Deadband
        # response = self.com.send("DB=8")
        # # Debounce home
        # response = self.com.send("D1=5")
        # # Set hold current
        # response = self.com.send("HC=20")
        # # Set run current
        # response = self.com.send("RC=100")

        # # Home stage program
        # self.com.send("PG 1")
        # self.com.send("HM 1")
        # self.com.send("H")
        # self.com.send("P = 30000")
        # self.com.send("E")
        # self.com.send("PG")
        # self.com._serial.flush()

        # Check if stage is homed correctly
        self.com.send("EX 1")  # Execute home stage program
