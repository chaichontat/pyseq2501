from concurrent.futures import Future
from contextlib import contextmanager
from logging import getLogger
from typing import Callable, Generator, Literal, Optional

from pyseq2.base.instruments import FPGAControlled, Movable
from pyseq2.com.async_com import CmdParse
from pyseq2.utils.utils import chkrng, ok_if_match, ok_re

logger = getLogger(__name__)


Y_OFFSET = int(7e6)
RANGE = (0, 65535)


class ObjCmd:
    # fmt: off
    # Callable[[Annotated[int, "mm/s"]], str]
    SET_VELO = CmdParse(lambda x: f"ZSTEP {int(1288471 * x)}", ok_if_match("ZSTEP"))
    SET_POS  = CmdParse(chkrng(lambda x: f"ZDACW {x}", *RANGE), ok_if_match("ZDACW"))
    GET_TARGET_POS = CmdParse(     "ZDACR"              , ok_re(r"^ZDACR (\d+)$", int))  # D A
    GET_POS        = CmdParse(     "ZADCR"              , ok_re(r"^ZADCR (\d+)$", int))  # A D
    
    # Autofocus stuffs
    SET_TRIGGER = CmdParse(lambda x: f"ZTRG {x}"   , ok_if_match("ZTRG"))
    ARM_TRIGGER = CmdParse(           "ZYT 0 3"    , ok_if_match("ZYT"))
    Z_MOVE      = CmdParse(lambda x: f"ZMV {x}"    , ok_if_match("@LOG Trigger Camera\nZMV"), n_lines=2)
    SWYZ        = CmdParse(           "SWYZ_POS 1" , ok_if_match("SWYZ_POS"))
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

    @contextmanager
    def af_arm(
        self, z_min: int = 2621, z_max: int = 60292
    ) -> Generator[Callable[[], Future[bool]], None, None]:
        try:
            self.com.send(ObjCmd.SET_POS(z_max)).result()  # Returns when done.
            self.com.send(ObjCmd.SWYZ)
            self.com.send(ObjCmd.SET_VELO(0.42))
            self.com.send(ObjCmd.SET_TRIGGER(z_max))
            self.com.send(ObjCmd.ARM_TRIGGER).result()
            yield lambda: self.com.send(ObjCmd.Z_MOVE(z_min))
        finally:
            self.com.send(ObjCmd.SET_VELO(5)).result()

    @property
    def is_moving(self) -> Future[Literal[False]]:
        return self.com._executor.submit(lambda: False)
