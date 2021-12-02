from __future__ import annotations

import asyncio
from concurrent.futures import Future
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
from returns.result import Result, Success, Failure

from serial_asyncio import open_serial_connection
from src.base.instruments_types import SerialInstruments
from src.utils.eventloop import LOOP

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
          y=lambda x: f"1{x}\r\n",  # Axis 1
    laser_g=lambda x:  f"{x}\r",
    laser_r=lambda x:  f"{x}\r",
)  # type: ignore
# fmt:on
T = TypeVar("T", covariant=True)
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
        Necessary conditions:
        - Commands are executed in FIFO order.
        - Response from an instrument is in FIFO order.
        - All responses are accounted for.

        Args:
            name (SerialInstruments): Name of the instrument.
            port_tx (str): COM port.
            port_rx (Optional[str], optional): Receiving port if different from port_tx.
                Only the FPGA uses separate channels.
            min_spacing (int, optional): Minimum time between commands. Defaults to 0.05s.
        """
        assert port_tx.startswith("COM")
        self.port = port_tx
        self.name = f"[{COLOR[name]}]{name:10s}[/{COLOR[name]}]"
        self.formatter = FORMATTER[name]

        self.min_spacing = min_spacing
        self.t_lastcmd = time.monotonic()

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
        self.tasks = (
            LOOP.put(self._read_forever()),
            LOOP.put(self._write_forever()),
        )  # Prevent garbage collection.
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
                await asyncio.sleep(max(0, self.min_spacing - (time.monotonic() - self.t_lastcmd)))
            self._serial.writer.write(self.formatter(msg).encode())
            self.t_lastcmd = time.monotonic()
            self._write_queue.task_done()
            logger.debug(f"{self.name}Tx: {msg}")

    @overload
    async def _send(self, msg: str) -> None:
        ...

    @overload
    async def _send(self, msg: CmdParse[T, Any]) -> Optional[T]:
        ...

    async def _send(self, msg: str | CmdParse[T, Any]) -> None | Optional[T]:
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
    def send(self, msg: CmdParse[T, Any]) -> Future[Optional[T]]:
        ...

    @overload
    def send(self, msg: tuple[str, ...]) -> tuple[None, ...]:
        ...

    @overload
    def send(self, msg: tuple[str | CmdParse[Any, Any], ...]) -> tuple[None | Future[Optional[Any]], ...]:
        ...

    @overload
    def send(self, msg: tuple[CmdParse[Any, Any], ...]) -> tuple[Future[Optional[Any]], ...]:
        ...

    @overload
    def send(self, msg: tuple[CmdParse[T, Any], ...]) -> tuple[Future[Optional[T]], ...]:
        ...

    def send(
        self, msg: str | CmdParse[T, Any] | tuple[str | CmdParse[Any, Any], ...]
    ) -> None | Future[Optional[T]] | tuple[None | Future[Optional[Any]], ...]:
        """Send command to instrument.
        If msg is string   => no responses expected.
        If msg is CmdParse => response expected and parsed by CmdParse.parser.
            Unexpected response triggers a warning and returns Future[None].
        If msg is a list of either above, map this function to all elements.

        Returns:
            None for msg, Future of a CmdParse result.
        """
        if isinstance(msg, str):
            LOOP.put(self._send(msg))
            return
        if isinstance(msg, CmdParse):
            return LOOP.put(self._send(msg))

        return tuple(self.send(x) for x in msg)


if __name__ == "__main__":
    g = COM(name="laser_g", port_tx="COM15")
    r = COM(name="laser_r", port_tx="COM17")

    ver = CmdParse("VERSION?\r", lambda x: x == "SMD-G-1.1.2")
    test = g.send(ver)
    test = r.send(ver)
    print(test.result())
    time.sleep(1)
    LOOP.stop()
