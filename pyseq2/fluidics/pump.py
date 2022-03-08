from __future__ import annotations

import asyncio
import logging
from contextlib import asynccontextmanager
from typing import Annotated, AsyncGenerator, Callable, ClassVar, Literal, TypeVar, cast

from pyseq2.base.instruments import UsesSerial
from pyseq2.com.async_com import COM, CmdParse
from pyseq2.utils.utils import IS_FAKE, ok_re

logger = logging.getLogger(__name__)


Sps = Annotated[int, "steps/sec"]
Step = Annotated[int, "step"]


def status_byte(s: str) -> bool:
    match s:
        case "@":
            return False
        case "`":
            return True
        case x:
            raise Exception(f"Pump has some error {x}.")


T = TypeVar("T")
parser = ok_re(r"/0([`@])", status_byte)


def check_range(prefix: Literal["pull", "push"]) -> Callable[[Step, Sps], str]:
    def inner(pos: Step, sps: Sps = 8000) -> str:
        if not 60 <= sps <= 8000:
            raise ValueError("Invalid speed. Range is [60, 8000].")
        if not 0 <= pos <= 48000:
            raise ValueError("Invalid position. Range is [0, 48000].")

        if prefix == "pull":
            return f"V{sps}IA{pos}R"
        elif prefix == "push":
            return f"V{sps}OA{pos}R"
        else:
            raise ValueError("Invalid command.")

    return inner


class PumpCmd:
    """
    https://www.jascoint.co.jp/products/contact-angle/pdf/ap48.pdf
    R = Execute
    O = Set valve to output
    I = Set valve to input
    V = Set speed
    A = Set volume
    Instructions can be combined and finished with R.
    """

    INIT = CmdParse("W4R", parser)
    STATUS = CmdParse("", parser)
    GET_POS = CmdParse("?", ok_re(r"/0[`@](\d+)", int))
    PULL = CmdParse(check_range("pull"), parser)
    PUSH = CmdParse(check_range("push"), parser)
    STOP = CmdParse("T", parser)


class Pump(UsesSerial):
    STEPS = 48000
    BARREL_VOL = 250
    PULL_SPEED = 1000
    PUSH_SPEED: ClassVar[Sps] = 8000

    @classmethod
    async def ainit(cls, name: Literal["pumpa", "pumpb"], port_tx: str) -> Pump:
        self = cls(cast(Literal["A", "B"], name[-1].upper()))
        self.com = await COM.ainit(name, port_tx)
        return self

    def __init__(self, name: Literal["A", "B"]) -> None:
        self.com: COM
        self.name = name

    async def wait(self, retries: int = 10) -> None:
        for _ in range(retries):
            if await self.com.send(PumpCmd.STATUS):
                return
            else:
                await asyncio.sleep(0.25)
        else:
            raise TimeoutError(f"Pump {self.name} not ready after too long.")

    async def initialize(self) -> None:
        async with self.com.big_lock:
            logger.info(f"Initializing pump {self.name}.")
            await self.com.send(PumpCmd.INIT)
            await asyncio.sleep(1)
            await self._pushpull("push", 0)
            logger.info(f"Pump {self.name} initialized.")

    @property
    async def pos(self) -> int:
        return await self.com.send(PumpCmd.GET_POS)

    @property
    async def status(self) -> bool:
        return await self.com.send(PumpCmd.STATUS)

    async def _pushpull(
        self, cmd: Literal["push", "pull"], target: int, *, speed: int = 8000, retries: int = 10
    ) -> None:
        await asyncio.wait_for(self.wait(), timeout=30)
        async with self.com.big_lock:
            pos = await self.pos
            match cmd:
                case "pull":
                    if pos >= target:
                        raise ValueError(
                            f"Current pump pos of {pos} greater than the requested pull pos of {target}."
                        )
                    await self.com.send(PumpCmd.PULL(target, speed))
                case "push":
                    if pos <= target:
                        raise ValueError(
                            f"Current pump pos of {pos} smaller than the requested push pos of {target}."
                        )
                    await self.com.send(PumpCmd.PUSH(target, speed))
                case _:
                    raise ValueError("Invalid command.")

        if not IS_FAKE():
            # logger.debug("Pump {self.name}: Waiting for pumping to finish.")
            await asyncio.sleep(abs(target - pos) / speed + 0.5)
        await self.wait(retries=retries)

    @asynccontextmanager
    async def _pump(self, vol: Step, *, v_pull: Sps = 400, v_push: Sps = 6400) -> AsyncGenerator[None, None]:
        try:
            logger.info(f"Pump {self.name}: Pulling.")
            await self._pushpull("pull", vol, speed=v_pull)
            logger.info(f"Pump {self.name}: Pull completed.")
            yield
        finally:
            logger.info(f"Pump {self.name}: Pushing.")
            await self._pushpull("push", 0, speed=v_push)
            logger.info(f"Pump {self.name}: Push completed.")

    async def pump(
        self, vol: Step, *, v_pull: Sps = 400, v_push: Sps = 6400, wait: Annotated[float, "s"] = 26
    ) -> None:
        if (pos := await self.pos) != 0:
            logger.warning(f"Pump {self.name} was not fully pulled out at start but at pos {pos}.")

        async with self._pump(vol, v_pull=v_pull, v_push=v_push):
            logger.info(f"Pump {self.name}: Waiting for {wait} s.")
            await asyncio.sleep(wait)  # From HiSeq log. Wait for pressure to equalize.
