import asyncio
import random
import time
from asyncio import StreamReader, StreamWriter
from logging import getLogger
from typing import Callable, Literal, Optional

from pyseq2.base.instruments_types import SEPARATOR, SerialInstruments
from pyseq2.fakes.fake_handlers import fake_arm9, fake_fpga, fake_laser, fake_pump, fake_valve, fake_x, fake_y

handlers: dict[SerialInstruments, Callable[[str], str]] = {
    "x": fake_x,
    "y": fake_y,
    "laser_g": fake_laser,
    "laser_r": fake_laser,
    "arm9chem": fake_arm9,
    "pumpa": fake_pump,
    "pumpb": fake_pump,
    "valve_a1": fake_valve,
    "valve_a2": fake_valve,
    "valve_b1": fake_valve,
    "valve_b2": fake_valve,
    "fpga": fake_fpga,
}

logger = getLogger(__name__)


class FakeTransport(asyncio.Transport):
    def __init__(
        self,
        loop: asyncio.AbstractEventLoop,
        protocol: asyncio.StreamReaderProtocol,
        name: SerialInstruments,
        test_params: Optional[dict] = None,
    ):
        super().__init__()
        self._name = name
        self._loop = loop
        self._protocol = protocol
        self.f = handlers[name]
        self.test_params = test_params
        self.sep = SEPARATOR.get(name, b"\n")

        self.q_rcvd: asyncio.Queue[bytes] = asyncio.Queue()

        loop.call_soon(protocol.connection_made, self)
        asyncio.create_task(self._process_forever())

    async def _process_forever(self):
        while True:
            try:
                cmd = await self.q_rcvd.get()
                self._protocol.data_received(cmd)  # Data received from the serial port.
                self.q_rcvd.task_done()
            except BaseException as e:
                logger.critical(f"{type(e).__name__}: {e}")

    def write(self, data: bytes):
        for res in self.f(data.strip().decode("ISO-8859-1")).split("\n"):
            # if time.time() - self.t0 < 5 or random.randint(0, 1):
            self.q_rcvd.put_nowait(res.encode("ISO-8859-1") + self.sep)


async def open_fake(
    url: str, name: SerialInstruments, baudrate: Literal[9600, 115200], test_params: Optional[dict] = None
) -> tuple[StreamReader, StreamWriter]:
    loop = asyncio.get_event_loop()
    reader = asyncio.StreamReader(loop=loop)
    protocol = asyncio.StreamReaderProtocol(reader, loop=loop)
    writer = asyncio.StreamWriter(FakeTransport(loop, protocol, name, test_params), protocol, reader, loop)
    return reader, writer


async def test():
    reader, writer = await open_fake("COMX", "fpga", 9600, {})
    writer.write(b"RESET")
    print(await reader.readline())
    # print("Waiting for 1 second.")
    # t = asyncio.create_task(reader.readline())
    # await asyncio.sleep(0.5)
    # writer.write(b"echoooo\n")
    # await asyncio.sleep(0.5)
    # print(await t)


if __name__ == "__main__":
    asyncio.run(test())
