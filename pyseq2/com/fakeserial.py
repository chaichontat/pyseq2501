import asyncio
from asyncio import StreamReader, StreamWriter
from typing import Literal

from pyseq2.base.instruments_types import SerialInstruments


class FakeTransport(asyncio.Transport):
    def __init__(
        self,
        loop: asyncio.AbstractEventLoop,
        protocol: asyncio.StreamReaderProtocol,
        name: SerialInstruments,
        test_params: dict,
    ):
        super().__init__()
        self._name = name
        self._loop = loop
        self._protocol = protocol
        self.test_params = test_params

        self.q_rcvd: asyncio.Queue[bytes] = asyncio.Queue()

        loop.call_soon(protocol.connection_made, self)
        asyncio.create_task(self._process_forever())

    async def _process_forever(self):
        while True:
            cmd = await self.q_rcvd.get()
            self._protocol.data_received(cmd)  # Data received from the serial port.
            self.q_rcvd.task_done()

    def write(self, data: bytes):
        self.q_rcvd.put_nowait(data)


FPGAChannel: tuple[StreamReader, StreamWriter] | None = None


async def open_serial_connection(
    url: str, name: SerialInstruments, baudrate: Literal[9600, 115200], test_params: dict
) -> tuple[StreamReader, StreamWriter]:
    global FPGAChannel  # FPGA uses separate ports for input/output.
    if name == "fpga" and FPGAChannel is not None:
        return FPGAChannel
    loop = asyncio.get_event_loop()
    reader = asyncio.StreamReader(loop=loop)
    protocol = asyncio.StreamReaderProtocol(reader, loop=loop)
    writer = asyncio.StreamWriter(FakeTransport(loop, protocol, name, test_params), protocol, reader, loop)
    if name == "fpga":
        FPGAChannel = (reader, writer)
    return reader, writer


async def test():
    reader, writer = await open_serial_connection("COMX", "fpga", 9600, {})
    writer.write(b"RESET\n")
    print(await reader.readline())
    print("Waiting for 1 second.")
    t = asyncio.create_task(reader.readline())
    await asyncio.sleep(0.5)
    writer.write(b"echoooo\n")
    await asyncio.sleep(0.5)
    print(await t)


if __name__ == "__main__":
    asyncio.run(test())
