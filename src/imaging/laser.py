import time
from concurrent.futures import Future
from dataclasses import dataclass
from logging import getLogger
from typing import Annotated

from returns.result import Failure, Result, ResultE, Success, safe
from src.instruments import UsesSerial
from src.utils.com import COM, CmdParse, is_between
from src.utils.utils import gen_future

logger = getLogger("laser")


class LaserCmd:
    @staticmethod
    def v_get_status(resp: str) -> Result[bool, Exception]:
        try:
            return Success({"DISABLED": False, "ENABLED": True}[resp])
        except KeyError:
            return Failure(Exception("Invalid laser response"))

    @staticmethod
    @safe
    def v_get_power(resp: str) -> int:
        assert resp.endswith("mW")
        return int(resp[:4])

    ON = "ON"
    OFF = "OFF"
    SET_POWER = lambda x: f"POWER={x}"
    GET_POWER = CmdParse("POWER?", v_get_power)
    GET_STATUS = CmdParse("STAT?", v_get_status)


class Laser(UsesSerial):
    POWER_RANGE = (0, 500)

    def __init__(self, port_tx: str) -> None:
        self.com = COM("laser_r", port_tx=port_tx, logger=logger)  # Doesn't matter if laser_r or g.
        self._on = False
        self.com.repl(LaserCmd.GET_STATUS).add_done_callback(lambda x: setattr(self, "_on", x.result()))

    def initialize(self) -> Future[str]:
        self.com.repl(LaserCmd.ON)
        return self.com.repl(LaserCmd.SET_POWER(1))

    def set_power(self, power: Annotated[int, "mW"], tol: Annotated[int, "mW"] = 3) -> Future[int]:
        self.com.repl(is_between(LaserCmd.SET_POWER, *self.POWER_RANGE)(power))
        return self.com.repl(LaserCmd.GET_POWER, lambda x: abs(power - x) < tol, attempts=5)

    @property
    def power(self) -> Future[int]:
        return self.com.repl(LaserCmd.GET_POWER)

    @property
    def on(self) -> bool:
        return self._on

    @on.setter
    def on(self, state: bool):
        self.set_onoff(state)

    def set_onoff(self, state: bool) -> Future[bool]:
        if state == self._on:
            return gen_future(state)
        self.com.repl({False: LaserCmd.OFF, True: LaserCmd.ON}[state])
        fut = self.com.repl(LaserCmd.GET_STATUS, lambda x: x == state, attempts=2)
        fut.add_done_callback(lambda x: setattr(self, "_on", x.result()))
        return fut


@dataclass
class Lasers:
    g: Laser
    r: Laser

    def initialize(self) -> None:
        self.g.initialize()
        self.r.initialize()
