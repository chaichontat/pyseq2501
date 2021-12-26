import re
from concurrent.futures import Future
from logging import getLogger
from typing import Optional

from pyseq2.base.instruments import FPGAControlled, Movable
from pyseq2.com.async_com import CmdParse
from pyseq2.com.thread_mgt import run_in_executor
from pyseq2.utils.utils import chkrng, ok_if_match, ok_re

logger = getLogger(__name__)


Y_OFFSET = int(7e6)
RANGE = (0, 65535)


class ObjCmd:
    # Callable[[Annotated[int, "mm/s"]], str]
    # fmt: off
    SET_VELO = CmdParse(lambda x: f"ZSTEP {1288471 * x}", ok_if_match("ZSTEP"))
    SET_POS  = CmdParse(chkrng(lambda x: f"ZDACW {x}", *RANGE), ok_if_match("ZDACW"))
    GET_TARGET_POS = CmdParse(     "ZDACR"              , ok_re(r"^ZDACR (\d+)$", int))
    GET_POS        = CmdParse(     "ZADCR"              , ok_re(r"^ZADCR (\d+)$", int))
    
    SET_TRIGGER = lambda x: f"ZTRG {x}"
    ARM_TRIGGER = "ZYT 0 3"
    # fmt: on


class ZObj(FPGAControlled, Movable):
    STEPS_PER_UM = 262
    RANGE = (0, 65535)
    HOME = 65535

    cmd = ObjCmd

    def initialize(self) -> Future[bool | None]:
        return self.com.send(ObjCmd.SET_VELO(5))

    @property
    def pos(self) -> Future[Optional[int]]:
        return self.com.send(ObjCmd.GET_POS)

    @pos.setter
    def pos(self, x: int) -> None:
        self.move(x)

    def move(self, x: int) -> Future[bool]:
        return self.com.send(ObjCmd.SET_POS(x))

    @property
    @run_in_executor
    def is_moving(self) -> bool:
        return self.pos.result(60) != self.pos.result(60)
