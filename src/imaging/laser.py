from dataclasses import dataclass, fields
import time

from concurrent.futures import Future
from logging import getLogger
from typing import Annotated, Any, Literal

from src.base.instruments import UsesSerial
from src.com.async_com import COM, CmdParse
from src.utils.utils import chkrng, ok_if_match
from src.com.thread_mgt import run_in_executor

logger = getLogger("Laser")
POWER_RANGE = (0, 500)


class LaserException(Exception):
    ...


class LaserCmd:
    """Laser commands

    Returns:
        [type]: [description]
    """

    @staticmethod
    def v_get_status(resp: str) -> None | bool:
        try:
            return {"DISABLED": False, "ENABLED": True}[resp]
        except KeyError:  # Tend to have status error on first calls.
            return None

    @staticmethod
    def v_get_power(resp: str) -> int:
        assert resp.endswith("mW")
        return int(resp[:4])

    # fmt: off
    ON = "ON"
    OFF = "OFF"
    SET_POWER  = chkrng(lambda x: f"POWER={x}", *POWER_RANGE) 
    GET_POWER  = CmdParse("POWER?"  , v_get_power)
    GET_STATUS = CmdParse("STAT?"   , v_get_status)
    VERSION    = CmdParse("VERSION?", ok_if_match(("SMD-G-1.1.2", "SMD-G-1.1.1")))
    # fmt: on


class Laser(UsesSerial):

    cmd = LaserCmd

    def __init__(self, name: Literal["laser_r", "laser_g"], port_tx: str) -> None:
        self.com = COM(name, port_tx=port_tx, min_spacing=0.1)
        self.initialize()

    @run_in_executor
    def initialize(self) -> None:
        self.com.send(LaserCmd.VERSION)
        self.set_onoff(True)

    @run_in_executor
    def set_onoff(self, state: bool, attempts: int = 3) -> bool:
        for i in range(attempts):
            if i > 0:
                logger.warning(f"Laser did not switch to {state}, Trying again.")
            self.com.send({False: LaserCmd.OFF, True: LaserCmd.ON}[state])
            while (resp := self.on.result(5)) is None:
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
        self, power: Annotated[int, "mW"], tol: Annotated[int, "mW"] = 3, timeout: Annotated[int, "s"] = 30
    ):
        """Laser can take a while to warm up.

        Args:
            power (int): [description]
            tol (int): [description]. Defaults to 3.
        """
        assert all((int(power) == power and power > 0, timeout > 0, tol > 0))
        if not self.on:
            self.set_onoff(True).result(5)
        self.com.send(LaserCmd.SET_POWER(power))

        for _ in range(timeout):
            time.sleep(1)
            if abs(power - self.power.result(5)) < tol:
                return True
        else:
            return False

    @property
    def on(self) -> Future[None | bool]:
        return self.com.send(LaserCmd.GET_STATUS)

    @property
    def power(self) -> Future[int]:
        return self.com.send(LaserCmd.GET_POWER)


@dataclass
class Lasers:
    g: Laser
    r: Laser

    def initialize(self) -> list[Future[Any]]:
        return [getattr(self, f.name).initialize() for f in fields(self)]
