import time
from concurrent.futures import Future, ThreadPoolExecutor
from dataclasses import dataclass
from logging import getLogger
from typing import Annotated, Literal

from src.instruments import UsesSerial
from src.utils.async_com import COM, CmdParse
from src.utils.utils import gen_future, is_between, run_in_executor

logger = getLogger("Laser")


class LaserCmd:
    @staticmethod
    def v_get_status(resp: str) -> bool:
        return {"DISABLED": False, "ENABLED": True, "Error:- 00": None}[resp]

    @staticmethod
    def v_get_power(resp: str) -> int:
        assert resp.endswith("mW")
        return int(resp[:4])

    ON = "ON"
    OFF = "OFF"
    SET_POWER = lambda x: f"POWER={x}"
    GET_POWER = CmdParse("POWER?", v_get_power)
    GET_STATUS = CmdParse("STAT?", v_get_status)
    VERSION = CmdParse("VERSION?", lambda x: {"SMD-G-1.1.2": True}[x])


class Laser(UsesSerial):
    """Need some spacing between commands."""

    POWER_RANGE = (0, 500)
    cmd = LaserCmd

    def __init__(self, name: Literal["laser_r", "laser_g"], port_tx: str) -> None:
        self.com = COM(name, port_tx=port_tx, min_spacing=0.1)
        self._on = False
        self._executor = ThreadPoolExecutor(max_workers=1)
        self.initialize()

    @run_in_executor
    def initialize(self) -> None:
        self.com.send(LaserCmd.ON)
        while (stat := self.com.send(LaserCmd.GET_STATUS).result()) is None:
            ...
        self._on = stat

    @property
    def power(self) -> Future[None | int]:
        return self.com.send(LaserCmd.GET_POWER)

    def set_power(self, power: Annotated[int, "mW"], tol: Annotated[int, "mW"] = 3):
        self.com.send(is_between(LaserCmd.SET_POWER, *self.POWER_RANGE)(power))
        # return self.com.send(LaserCmd.GET_POWER, lambda x: abs(power - x) < tol, attempts=5)

    @property
    def on(self) -> None | bool:
        return self._on

    @on.setter
    def on(self, state: bool):
        self.set_onoff(state)

    def set_onoff(self, state: bool) -> Future[bool | None]:
        if state == self._on:
            return gen_future(state)
        self.com.send({False: LaserCmd.OFF, True: LaserCmd.ON}[state])
        fut = self.com.send(LaserCmd.GET_STATUS)
        fut.add_done_callback(lambda x: setattr(self, "_on", x.result()))
        return fut


@dataclass
class Lasers:
    g: Laser
    r: Laser

    def initialize(self) -> None:
        self.g.initialize()
        self.r.initialize()
