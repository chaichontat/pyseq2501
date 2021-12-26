import time
from concurrent.futures import Future
from dataclasses import dataclass, fields
from logging import getLogger
from typing import Annotated, Any, Literal

from pyseq2.base.instruments import UsesSerial
from pyseq2.com.async_com import COM, CmdParse
from pyseq2.com.thread_mgt import run_in_executor
from pyseq2.utils.utils import chkrng, not_none, ok_if_match

logger = getLogger(__name__)
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

    @run_in_executor
    def set_onoff(self, state: bool, attempts: int = 3) -> bool:
        for i in range(attempts):
            if i > 0:
                logger.warning(f"Laser did not switch to {state}, Trying again.")
            self.com.send({False: LaserCmd.OFF, True: LaserCmd.ON}[state])
            while (resp := self.status.result(5)) is None:
                ...
            if resp == state:
                break
        else:
            raise LaserException(
                f"Laser did not switch to {state} after {attempts} attempts. Check if all doors are 'closed'."
            )
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
            if abs(power - not_none(self.power.result(5))) < tol:
                return True
        else:
            return False

    @property
    def status(self) -> Future[None | bool]:
        return self.com.send(LaserCmd.GET_STATUS)

    def on(self) -> Future[bool]:
        return self.set_onoff(True)

    def off(self) -> Future[bool]:
        return self.set_onoff(False)

    @property
    @run_in_executor
    def power(self) -> None | int:
        if self.status.result():
            return self.com.send(LaserCmd.GET_POWER).result()
        return None

    @power.setter
    def power(self, x: int) -> None:
        self.set_power(x)


@dataclass
class Lasers:
    g: Laser
    r: Laser

    def initialize(self) -> list[Future[Any]]:
        return [getattr(self, f.name).initialize() for f in fields(self)]

    def on(self):
        return (self.g.on(), self.r.on())

    def off(self):
        return (self.g.off(), self.r.off())
