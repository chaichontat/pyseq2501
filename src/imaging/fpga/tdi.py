import re
from concurrent.futures import Future
from logging import getLogger

from src.instruments import FPGAControlled
from src.utils.com import CmdParse, ok_if_match

logger = getLogger(__name__)


Y_OFFSET = int(7e6)


class TDICmd:
    @staticmethod
    def read_y(resp: str) -> int:
        match = re.match(r"^TDIYERD (\d+)$", resp)
        assert match is not None
        return int(match.group(1)) - Y_OFFSET

    GET_Y = CmdParse("TDIYERD", read_y)
    SET_Y = CmdParse(lambda x: f"TDIYPOS {x + Y_OFFSET - 80000}", ok_if_match("TDIYPOS"))
    ARM = lambda n, y: f"TDIYARM3 {n} {y + Y_OFFSET - 10000} 1"


class TDI(FPGAControlled):
    cmd = TDICmd

    def read_position(self) -> Future[int]:
        return self.fcom.repl(TDICmd.GET_Y)

    def write_position(self, position) -> Future[bool]:
        """Write the position of the y stage to the encoder.

        Allows for a 5 step (50 nm) error.

        **Parameters:**
         - position (int) = The position of the y stage.

        """
        return self.fcom.repl(TDICmd.SET_Y(position))

    def TDIYPOS(self, y_pos) -> Future[bool]:
        """Set the y position for TDI imaging.

        **Parameters:**
         - y_pos (int): The initial y position of the image.

        """
        return self.fcom.repl(TDICmd.SET_Y(y_pos))

    def TDIYARM3(self, n_triggers, y_pos) -> Future[str]:
        """Arm the y stage triggers for TDI imaging.

        **Parameters:**
         - n_triggers (int): Number of triggers to send to the cameras.
         - y_pos (int): The initial y position of the image.

        """
        return self.fcom.repl(TDICmd.ARM(n_triggers, y_pos))
