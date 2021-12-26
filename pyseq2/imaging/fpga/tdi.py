from concurrent.futures import Future
from logging import getLogger

from pyseq2.base.instruments import FPGAControlled
from pyseq2.com.async_com import CmdParse
from pyseq2.utils.utils import ok_if_match, ok_re

logger = getLogger(__name__)


Y_OFFSET = int(7e6)


class TDICmd:
    # fmt: off
    GET_ENCODER_Y = CmdParse(              "TDIYERD"                              , ok_re(r"TDIYERD (\d+)", lambda x: int(x) - Y_OFFSET))
    SET_ENCODER_Y = CmdParse(lambda x:    f"TDIYEWR {x + Y_OFFSET}"               , ok_if_match("TDIYEWR"))

    SET_TRIGGER   = CmdParse(lambda x:    f"TDIYPOS {x + Y_OFFSET - 80000}"       , ok_if_match("TDIYPOS"))
    WHATISTHIS             = lambda n:    f"TDIYARM2 {n} 1"
    ARM_TRIGGER   = CmdParse(lambda n, y: f"TDIYARM3 {n} {y + Y_OFFSET - 10000} 1", ok_if_match("TDIYARM3"))
    N_PULSES      = CmdParse(              "TDIPULSES"                            , ok_re(r"TDIPULSES (\d+)", lambda x: int(x) - 1))
    # fmt: on


# TDIYPOS == Set when to send first trigger aka starting position

# TDIYARM2 2816 Number of lines to capture. 22 frames V=0.115 Also with ZARM and ZYT ZFREQCL 10000
# Seems like Y scan with Z step occuring every end of scan.

# TDIYWAIT then immediately send Y move commands Seems to block thread until done.
#

# TDIYARM3 nlines  ZFREQCL 7500
# pos = TDIYPOS + 20813


class TDI(FPGAControlled):
    cmd = TDICmd

    @property
    def encoder_pos(self) -> Future[int]:
        return self.com.send(TDICmd.GET_ENCODER_Y)

    @encoder_pos.setter
    def encoder_pos(self, pos: int) -> None:
        self.com.send(TDICmd.SET_ENCODER_Y(pos))
        self._position = pos

    def prepare_for_imaging(self, n_px_y: int, pos: int) -> Future[bool]:
        self.encoder_pos = pos
        self.com.send(TDICmd.SET_TRIGGER(pos))
        return self.com.send(TDICmd.ARM_TRIGGER(n_px_y, pos))

    @property
    def n_pulses(self) -> Future[int]:
        return self.com.send(TDICmd.N_PULSES)
