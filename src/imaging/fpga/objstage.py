import re
from concurrent.futures import Future
from logging import getLogger
from typing import Optional

from src.base.instruments import FPGAControlled, Movable
from src.com.async_com import CmdParse
from src.com.thread_mgt import run_in_executor
from src.utils.utils import ok_if_match

logger = getLogger("objective")


Y_OFFSET = int(7e6)


class ObjCmd:
    @staticmethod
    def get_pos(resp: str) -> int:
        match = re.match(r"^ZDACR (\d+)$", resp)
        assert match is not None
        return int(match.group(1))

    # Callable[[Annotated[int, "mm/s"]], str]
    # fmt: off
    SET_VELO = CmdParse(lambda x: f"ZSTEP {1288471 * x}", ok_if_match("ZSTEP"))
    SET_POS  = CmdParse(lambda x: f"ZDACW {x}"          , ok_if_match("ZDACW"))
    GET_TARGET_POS = CmdParse(     "ZDACR"              , get_pos)
    GET_POS  = CmdParse(           "ZADCR"              , get_pos)
    
    SET_TRIGGER = lambda x: f"ZTRG {x}"
    ARM_TRIGGER = "ZYT 0 3"
    # fmt: on


class ObjStage(FPGAControlled, Movable):
    STEPS_PER_UM = 262
    RANGE = (0, 65535)
    HOME = 65535

    cmd = ObjCmd

    def initialize(self) -> Future[bool | None]:
        return self.com.send(ObjCmd.SET_VELO(5))

    @property
    def position(self) -> Future[Optional[int]]:
        return self.com.send(ObjCmd.GET_POS)

    def move(self, x: int) -> Future[None | bool]:
        return self.com.send(ObjCmd.SET_POS(x))

    @property
    @run_in_executor
    def is_moving(self) -> bool:
        return self.position.result() != self.position.result()
