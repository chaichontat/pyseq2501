import re
from concurrent.futures import Future
from logging import getLogger

from src.instruments import FPGAControlled
from src.utils.com import COM, CmdParse, ok_if_match

logger = getLogger(__name__)


Y_OFFSET = int(7e6)


class TDICmd:
    @staticmethod
    def read_y(resp: str) -> int:
        match = re.match(r"^TDIYERD (\d+)$", resp)
        assert match is not None
        return int(match.group(1)) - Y_OFFSET

    # fmt: off
    GET_ENCODER_Y = CmdParse(              "TDIYERD"                            , read_y)
    SET_ENCODER_Y =          lambda x:    f"TDIYEWR      {x + Y_OFFSET}"

    SET_Y_POS     = CmdParse(lambda x:    f"TDIYPOS      {x + Y_OFFSET - 80000}", ok_if_match("TDIYPOS"))
    ARM                    = lambda n, y: f"TDIYARM3 {n} {y + Y_OFFSET - 10000} 1"
    # fmt: on


class TDI(FPGAControlled):
    cmd = TDICmd

    def __init__(self, fpga_com: COM) -> None:
        super().__init__(fpga_com)
        self._position: int
        # self.fcom.repl(TDICmd.GET_ENCODER_Y).add_done_callback(
        #     lambda x: setattr(self, "_position", x.result())
        # )

    @property
    def encoder_pos(self):
        return self._position

    @encoder_pos.setter
    def encoder_pos(self, pos: int):
        self.fcom.repl(TDICmd.SET_ENCODER_Y(pos))
        self._position = pos

    def prepare_for_imaging(self, n_px_y: int, pos: int) -> Future[str]:
        self.encoder_pos = pos
        self.fcom.repl(TDICmd.SET_Y_POS(pos))
        return self.fcom.repl(TDICmd.ARM(n_px_y, pos))

    # def TDIYPOS(self, y_pos) -> Future[bool]:
    #     """Set the y position for TDI imaging.

    #     **Parameters:**
    #      - y_pos (int): The initial y position of the image.

    #     """
    #     return self.fcom.repl(TDICmd.SET_Y_POS(y_pos))

    # def TDIYARM3(self, n_triggers, y_pos) -> Future[str]:
    #     """Arm the y stage triggers for TDI imaging.

    #     **Parameters:**
    #      - n_triggers (int): Number of triggers to send to the cameras.
    #      - y_pos (int): The initial y position of the image.

    #     """
    #     return self.fcom.repl(TDICmd.ARM(n_triggers, y_pos))
