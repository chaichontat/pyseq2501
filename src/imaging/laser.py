from dataclasses import dataclass, fields
import time

from concurrent.futures import Future, ThreadPoolExecutor
from logging import getLogger
from typing import Annotated, Any, Literal

from src.base.instruments import UsesSerial
from src.com.async_com import COM, CmdParse
from src.utils.utils import is_between
from src.com.thread_mgt import run_in_executor

logger = getLogger("Laser")


class LaserException(Exception):
    ...


class LaserCmd:
    """Laser commands

    Returns:
        [type]: [description]
    """

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
    VERSION = CmdParse("VERSION?", lambda x: {"SMD-G-1.1.2": True, "SMD-G-1.1.1": True}[x])


class Laser(UsesSerial):
    POWER_RANGE = (0, 500)
    cmd = LaserCmd

    def __init__(self, name: Literal["laser_r", "laser_g"], port_tx: str) -> None:
        self.com = COM(name, port_tx=port_tx, min_spacing=0.1)
        self.initialize()

    @run_in_executor
    def initialize(self) -> None:
        self.com.send(LaserCmd.VERSION)
        self.set_onoff(True)

    @property
    def power(self) -> Future[None | int]:
        return self.com.send(LaserCmd.GET_POWER)

    @run_in_executor
    def set_onoff(self, state: bool, attempts: int = 3) -> bool:
        if state == self._on:
            return state
        for i in range(attempts):
            if i > 0:
                logger.warning(f"Laser did not switch to {state}, Trying again.")
            self.com.send({False: LaserCmd.OFF, True: LaserCmd.ON}[state])
            while (resp := self.com.send(LaserCmd.GET_STATUS).result()) is None:
                ...
            if resp == state:
                break
        else:
            raise LaserException(
                f"Laser did not switch to {state} after {attempts} attempts. Check if all doors are 'closed'."
            )
        self._on = state
        return resp

    @run_in_executor
    def set_power(
        self, power: Annotated[int, "mW"], tol: Annotated[int, "mW"] = 3, timeout: Annotated[int, "s"] = 10
    ):
        """Laser can take a while to warm up.

        Args:
            power (int): [description]
            tol (int): [description]. Defaults to 3.
        """
        p = None
        assert all((int(power) == power and power > 0, timeout > 0, tol > 0))
        if not self.on:
            self.set_onoff(True)
        self.com.send(is_between(LaserCmd.SET_POWER, *self.POWER_RANGE)(power))

        for _ in range(2 * timeout):
            time.sleep(1 / 2)
            p = self.com.send(LaserCmd.GET_POWER).result()
            assert p is not None
            if abs(power - p) < tol:
                return
        else:
            raise LaserException(f"Laser power not {power} mW after {timeout} seconds. Currently at {p} mW.")

    @property
    def on(self) -> None | bool:
        return self._on

    @on.setter
    def on(self, state: bool):
        self.set_onoff(state)


@dataclass
class Lasers:
    g: Laser
    r: Laser

    def initialize(self) -> list[Future[Any]]:
        return [getattr(self, f.name).initialize() for f in fields(self)]
