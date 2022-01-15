from __future__ import annotations

import asyncio
from dataclasses import dataclass
from logging import getLogger
from typing import Annotated, Literal, cast

from pyseq2.base.instruments import UsesSerial
from pyseq2.base.instruments_types import SerialInstruments
from pyseq2.com.async_com import COM, CmdParse
from pyseq2.utils.utils import chkrng, ok_if_match, λ_int

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
    def v_get_status(resp: str) -> bool:
        # Tend to have status error on first calls.
        return {"DISABLED": False, "ENABLED": True}.get(resp, False)

    @staticmethod
    def v_get_power(resp: str) -> int:
        assert resp.endswith("mW")
        return int(resp[:4])

    # fmt: off
    ON = "ON"
    OFF = "OFF"
    SET_POWER  = λ_int(chkrng(lambda x: f"POWER={x}", *POWER_RANGE))
    GET_POWER  = CmdParse("POWER?"  , v_get_power)
    GET_STATUS = CmdParse("STAT?"   , v_get_status)
    VERSION    = CmdParse("VERSION?", ok_if_match(("SMD-G-1.1.2", "SMD-G-1.1.1")))
    # fmt: on


class Laser(UsesSerial):

    cmd = LaserCmd

    @classmethod
    async def ainit(cls, name: Literal["r", "g"], port_tx: str) -> Laser:
        self = cls()
        self.com = await COM.ainit(cast(SerialInstruments, "laser_" + name), port_tx=port_tx, min_spacing=0.1)
        await self.initialize()
        return self

    def __init__(self) -> None:
        self.com: COM

    async def initialize(self) -> None:
        await self.com.send(LaserCmd.VERSION)

    async def set_onoff(self, state: bool, attempts: int = 3) -> None:
        for i in range(attempts):
            if i > 0:
                logger.warning(f"Laser did not switch to {state}, Trying again.")
            await self.com.send({False: LaserCmd.OFF, True: LaserCmd.ON}[state])
        #     while (resp := self.status.result(5)) is None:
        #         ...
        #     if resp == state:
        #         break
        # else:
        #     raise LaserException(
        #         f"Laser did not switch to {state} after {attempts} attempts. Check if all doors are 'closed'."
        #     )
        # return resp

    async def set_power(self, power: Annotated[int, "mW"], tol: Annotated[int, "mW"] = 3) -> None:
        """Laser can take a while to warm up.

        Args:
            power (int): [description]
            tol (int): [description]. Defaults to 3.
        """
        assert all((int(power) == power and power > 0, tol > 0))
        if not self.on:
            await self.set_onoff(True)
        await self.com.send(LaserCmd.SET_POWER(power))

        # for _ in range(timeout):
        #     time.sleep(1)
        #     if abs(power - not_none(self.power.result(5))) < tol:
        #         return True
        # else:
        #     return False

    @property
    async def status(self) -> bool:
        return await self.com.send(LaserCmd.GET_STATUS)

    async def on(self) -> None:
        return await self.set_onoff(True)

    async def off(self) -> None:
        return await self.set_onoff(False)

    @property
    async def power(self) -> int:
        return await self.com.send(LaserCmd.GET_POWER)

    @power.setter
    async def power(self, x: int) -> None:
        await self.set_power(x)


@dataclass
class Lasers:
    g: Laser
    r: Laser

    @property
    async def power(self) -> tuple[int, int]:
        return await asyncio.gather(self.g.power, self.r.power)

    # def initialize(self) -> list[Future[Any]]:
    #     return [getattr(self, f.name).initialize() for f in fields(self)]

    # def on(self):
    #     return (self.g.on(), self.r.on())

    # def off(self):
    #     return (self.g.off(), self.r.off())
