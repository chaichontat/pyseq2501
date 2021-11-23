import time
from concurrent.futures import Future
from logging import getLogger

from src.instruments import FPGAControlled

logger = getLogger(__name__)


Y_OFFSET = int(7e6)


class FPGACmd:
    READ_Y = "TDIYERD"
    SET_Y = lambda x: f"TDIYPOS {x}"
    ARM = lambda n, y: f"TDIYARM3 {n} {y + Y_OFFSET - 10000} 1"


class TDI(FPGAControlled):
    def initialize(self) -> Future[str]:
        return self.com.repl(FPGACmd.RESET)

    def read_position(self) -> Future[int]:
        """Read the y position of the encoder for TDI imaging.

        **Returns:**
         - int: The y position of the encoder.

        """
        return self.com.repl(FPGACmd.READ_Y).add_done_callback(
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
        return self.com.repl(FPGACmd.SET_Y(y_pos + Y_OFFSET - 80000))

    def TDIYARM3(self, n_triggers, y_pos) -> Future[str]:
        """Arm the y stage triggers for TDI imaging.

        **Parameters:**
         - n_triggers (int): Number of triggers to send to the cameras.
         - y_pos (int): The initial y position of the image.

        """
        return self.com.repl(FPGACmd.ARM(n_triggers, y_pos))
