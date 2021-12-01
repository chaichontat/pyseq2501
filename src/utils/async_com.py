from __future__ import annotations

import asyncio
import concurrent.futures
import queue
import time
from asyncio import StreamReader, StreamWriter
from dataclasses import dataclass
from logging import getLogger
from typing import (
    Annotated,
    Any,
    Callable,
    Generic,
    NamedTuple,
    NoReturn,
    Optional,
    ParamSpec,
    TypeVar,
    overload,
)

from rich.console import Console

console = Console()
from serial_asyncio import open_serial_connection
from src.eventloop import LOOP
from src.instruments_types import SerialInstruments

logger = getLogger("COM")
# fmt:off
# Pick from ANSI colors.
COLOR: dict[SerialInstruments, str] = dict(
    fpga="blue",
    x="purple",
    y="yellow",
    laser_g="green",
    laser_r="red"
) # type: ignore
FORMATTER: dict[SerialInstruments, Callable[[str], str]] = dict(
       fpga=lambda x:  f"{x}\n",
          x=lambda x:  f"{x}\r",
          y=lambda x: f"1{x}\r\n",
    laser_g=lambda x:  f"{x}\r",
    laser_r=lambda x:  f"{x}\r",
)  # type: ignore
# fmt:on
T = TypeVar("T")
P = ParamSpec("P")


class Channel(NamedTuple):
    reader: StreamReader
    writer: StreamWriter


@dataclass(frozen=True)
class CmdParse(Generic[T, P]):
    """A command with its parsing function.

    Args:
        cmd: String command or a unary function that outputs a command.
        process: A unary function that takes in raw output from the device and parse it into a useful format.
            Uses the Result architecture.

    Returns:
        A data structure where a command and its parsing function are together.
    """

    cmd: str | Callable[P, str]
    parser: Callable[[str], T]
    n_lines: int = 1

    def __call__(self, *args: P.args, **kwargs: P.kwargs) -> CmdParse[T, P]:
        if isinstance(self.cmd, str):
            raise TypeError("This command does not take argument(s).")
        return CmdParse(self.cmd(*args, **kwargs), self.parser)

    def __str__(self) -> str:
        return str(self.cmd)


class COM:
    def __init__(
        self,
        name: SerialInstruments,
        port_tx: str,
        port_rx: Optional[str] = None,
        min_spacing: Annotated[int | float, "s"] = 0.05,
    ) -> None:
        """
        Args:
            name (SerialInstruments): [description]
            port_tx (str): [description]
            port_rx (Optional[str], optional): [description]. Defaults to None.
            min_spacing (int, optional): Blocks calling thread between consecutive commands. Defaults to 0.
                Do not use this on the main thread.
        """
        assert port_tx.startswith("COM")
        self.port = port_tx
        self.name = f"[{COLOR[name]}]{name:10s}[/{COLOR[name]}]"
        self.formatter = FORMATTER[name]

        self.min_spacing = min_spacing
        self.t_lastcmd = time.time()

        # asyncio.Queue is not thread-safe and we're not waiting anyway.
        self._read_queue: queue.Queue[tuple[CmdParse, asyncio.Future]] = queue.Queue()
        self._write_queue: asyncio.Queue[str] = asyncio.Queue()
        if port_rx is not None:
            assert name == "fpga"
            srx = LOOP.put(open_serial_connection(url=port_rx, baudrate=115200))
            stx = LOOP.put(open_serial_connection(url=port_tx, baudrate=115200))
            self._serial = Channel(reader=srx.result()[0], writer=stx.result()[1])
            logger.info(f"{self.name}Started listening to ports {port_tx} and {port_rx}.")
        else:
            assert name != "fpga"
            self._serial = Channel(*LOOP.put(open_serial_connection(url=port_tx, baudrate=9600)).result())
            logger.info(f"{self.name}Started listening to port {port_tx}.")
        self.tasks = (LOOP.put(self._read_forever()), LOOP.put(self._write_forever()))
        time.sleep(0.1)  # Give time for read_forever to purge channel.

    async def _read_forever(self) -> NoReturn:
        while True:
            resp = (await self._serial.reader.readline()).decode().strip()
            if not resp:  # len == 0
                continue
            try:
                cmd, fut = self._read_queue.get_nowait()
            except queue.Empty:
                logger.warning(f"{self.name}Got mysterious return '{resp}'.")
                continue

            try:
                for _ in range(1, cmd.n_lines):
                    resp += "\n" + (await self._serial.reader.readline()).decode().strip()
                parsed = cmd.parser(resp)

            except:
                logger.error(f"{self.name}Exception while parsing '{resp}' from '{cmd.cmd}'.")
                # console.print_exception()
                fut.set_result(None)
            else:
                logger.debug(f"{self.name}Rx: {resp} [green] Verified")
                fut.set_result(parsed)
            finally:
                self._read_queue.task_done()

    async def _write_forever(self) -> NoReturn:
        while True:
            msg = await self._write_queue.get()
            if self.min_spacing:
                await asyncio.sleep(max(0, self.min_spacing - (time.time() - self.t_lastcmd)))
            self._serial.writer.write(self.formatter(msg).encode())
            self.t_lastcmd = time.time()
            self._write_queue.task_done()
            logger.debug(f"{self.name}Tx: {msg}")

    def _write(self, msg: str) -> None:
        if self.min_spacing:
            time.sleep(max(0, self.min_spacing - (time.time() - self.t_lastcmd)))
        self._serial.writer.write(self.formatter(msg).encode())
        self.t_lastcmd = time.time()
        logger.debug(f"{self.name}Tx: {msg}")

    async def _send(self, msg: str | CmdParse[T, P]) -> None | T:
        if isinstance(msg, str):
            self._write_queue.put_nowait(msg)
            return

        if not isinstance(msg.cmd, str):
            raise ValueError("This command needs argument(s), call it first.")

        self._write_queue.put_nowait(msg.cmd)
        self._read_queue.put_nowait((msg, fut := asyncio.Future()))
        return await fut

    @overload
    def send(self, msg: str) -> None:
        ...

    @overload
    def send(self, msg: CmdParse[T, P]) -> concurrent.futures.Future[None | T]:
        ...

    @overload
    def send(self, msg: list[str | CmdParse[Any, P]]) -> list[None | concurrent.futures.Future[None | Any]]:
        ...

    def send(
        self, msg: str | CmdParse[T, P] | list[str | CmdParse[T, P]]
    ) -> None | concurrent.futures.Future[None | Any] | list[None | concurrent.futures.Future[None | Any]]:
        if isinstance(msg, str):
            LOOP.put(self._send(msg))
            return
        if isinstance(msg, CmdParse):
            return LOOP.put(self._send(msg))

        return [self.send(x) for x in msg]


if __name__ == "__main__":
    g = COM(name="laser_g", port_tx="COM15")
    r = COM(name="laser_r", port_tx="COM17")

    ver = CmdParse("VERSION?\r", lambda x: x == "SMD-G-1.1.2")
    test = g.send(ver)
    test = r.send(ver)
    print(test.result())
    time.sleep(1)
    LOOP.stop()
