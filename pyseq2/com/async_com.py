from __future__ import annotations

import asyncio
import queue
import threading
import time
from asyncio import StreamReader, StreamWriter
from concurrent.futures import Future, ThreadPoolExecutor
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
    Sequence,
    TypeVar,
    overload,
)

from pyseq2.base.instruments_types import SerialInstruments
from pyseq2.com.eventloop import LOOP
from serial_asyncio import open_serial_connection

logger = getLogger(__name__)
# © is not in ASCII. Looking at you Schneider Electrics (x-stage).
ENCODING_KW = {"encoding": "ISO-8859-1", "errors": "replace"}
# fmt: off
# Pick from ANSI colors.
COLOR: dict[SerialInstruments, str] = dict(
    fpga="blue",
    x="purple",
    y="yellow",
    laser_g="green",
    laser_r="magenta"
)  # type: ignore
FORMATTER: dict[SerialInstruments, Callable[[str], str]] = dict(
       fpga=lambda x:  f"{x}\n",
          x=lambda x:  f"{x}\r",
          y=lambda x: f"1{x}\r\n",  # Axis 1
    laser_g=lambda x:  f"{x}\r",
    laser_r=lambda x:  f"{x}\r",
)   # type: ignore
# fmt: on
T = TypeVar("T", covariant=True)
P = ParamSpec("P")


def wait_results(futs: Sequence[Future[Any]]) -> Sequence[Any]:
    return [f.result() for f in futs]


class Channel(NamedTuple):
    reader: StreamReader
    writer: StreamWriter


@dataclass(frozen=True)
class CmdParse(Generic[T, P]):
    """A command with its parsing function.

    If the command is callable, this entire structure is callable and
    outputs the same structure but with an `str` command.

    Args:
        cmd: String command or a unary function that outputs a command.
        parser: A unary function that takes in raw output from the device and parse it into a useful format.
        n_lines: Number of lines in the expected response.

    Returns:
        A data structure in which a command and its parsing function are together.
    """

    cmd: str | Callable[P, str]
    parser: Callable[[str], T]
    n_lines: int = 1

    def __call__(self, *args: P.args, **kwargs: P.kwargs) -> CmdParse[T, P]:
        if isinstance(self.cmd, str):
            raise TypeError("This command does not take argument(s).")
        return CmdParse(self.cmd(*args, **kwargs), self.parser, n_lines=self.n_lines)

    def __str__(self) -> str:
        return str(self.cmd)


class COM:
    """
    Necessary conditions:
    - Commands are executed in FIFO order.
    - Response from an instrument is in FIFO order.
    - All responses are accounted for.

    Specific to each COM channel.

    Args:
        name (SerialInstruments): Name of the instrument.
        port_tx (str): COM port.
        port_rx (Optional[str], optional): Receiving port if different from port_tx.
            Only the FPGA uses separate channels.
        min_spacing (int, optional): Minimum time between commands. Defaults to 0.05s.
    """

    def __init__(
        self,
        name: SerialInstruments,
        port_tx: str,
        port_rx: Optional[str] = None,
        min_spacing: Annotated[int | float, "s"] = 0.05,
        no_check=False,
    ) -> None:

        self.port = port_tx
        self.name = f"[{COLOR[name]}]{name:10s}[/{COLOR[name]}]"
        self.formatter = FORMATTER[name]
        self.no_check = no_check

        self.min_spacing = min_spacing
        self.t_lastcmd = time.monotonic()
        self.lock = threading.RLock()
        self._executor = ThreadPoolExecutor(max_workers=1)

        # asyncio.Queue is not thread-safe and we're not waiting anyway.
        self._read_queue: queue.Queue[tuple[CmdParse, asyncio.Future]] = queue.Queue()
        if port_rx is not None:
            assert name == "fpga"
            srx = LOOP.put(open_serial_connection(url=port_rx, baudrate=115200))
            stx = LOOP.put(open_serial_connection(url=port_tx, baudrate=115200))
            self._serial = Channel(reader=srx.result(1)[0], writer=stx.result(1)[1])
            logger.info(f"{self.name}Started listening to ports {port_tx} and {port_rx}.")
        else:
            assert name != "fpga"
            self._serial = Channel(*LOOP.put(open_serial_connection(url=port_tx, baudrate=9600)).result(1))
            logger.info(f"{self.name}Started listening to port {port_tx}.")

        self.tasks = LOOP.put(self._read_forever())  # Prevents garbage collection.
        time.sleep(0.1)  # Give time for read_forever to purge channel.

    async def _read_forever(self) -> NoReturn:
        while True:
            resp = (await self._serial.reader.readline()).decode(**ENCODING_KW).strip()

            if self.no_check:
                print(resp)
                continue

            if not resp:  # len == 0
                continue
            try:
                cmd, fut = self._read_queue.get_nowait()
            except queue.Empty:
                logger.warning(f"{self.name}Got mysterious return '{resp}'.")
                continue

            try:
                for _ in range(1, cmd.n_lines):
                    resp += "\n" + (await self._serial.reader.readline()).decode(**ENCODING_KW).strip()
                parsed = cmd.parser(resp)
            except BaseException as e:
                logger.error(
                    f"{self.name}Exception {type(e).__name__} while parsing '{resp}' from '{cmd.cmd}'."
                )
                fut.set_exception(e)
            else:
                r = "'" + resp.replace("\n", "\\n") + "'"
                logger.debug(f"{self.name}Rx:  {r:20s} [green]Parsed: '{parsed}'")
                fut.set_result(parsed)
            finally:
                self._read_queue.task_done()

    @overload
    def send(self, msg: str) -> None:
        ...

    @overload
    def send(self, msg: CmdParse[T, Any]) -> Future[T]:
        ...

    @overload
    def send(self, msg: tuple[str, ...]) -> tuple[None, ...]:
        ...

    @overload
    def send(self, msg: tuple[str | CmdParse[Any, Any], ...]) -> tuple[None | Future[Any], ...]:
        ...

    @overload
    def send(self, msg: tuple[CmdParse[Any, Any], ...]) -> tuple[Future[Any], ...]:
        ...

    @overload
    def send(self, msg: tuple[CmdParse[T, Any], ...]) -> tuple[Future[T], ...]:
        ...

    def send(
        self, msg: str | CmdParse[T, Any] | tuple[str | CmdParse[Any, Any], ...]
    ) -> None | Future[T] | tuple[None | Future[Any], ...]:
        """Sends a command to an instrument.
        If msg is string   => no responses expected.
        If msg is CmdParse => response expected and parsed by CmdParse.parser.
            Unexpected response triggers a warning and returns Future[None].

        If msg is a list of either above, map this function to all elements.

        Returns:
            None for msg, Future of a CmdParse result.
        """
        with self.lock:  # Main thread and COM-specific thread can use this function at the same time.
            if isinstance(msg, str):
                self._send(self.formatter(msg).encode(**ENCODING_KW))
                return

            if isinstance(msg, CmdParse):
                if not isinstance(msg.cmd, str):
                    raise ValueError("This command needs argument(s), call it first.")

                self._read_queue.put_nowait((msg, fut := asyncio.Future(loop=LOOP.loop)))
                self._send(self.formatter(msg.cmd).encode(**ENCODING_KW))
                return LOOP.put(self.async_wrapper(fut))
            return tuple(self.send(x) for x in msg)

    def _send(self, msg: bytes) -> None:
        """This needs to be synchronous to maintain order of execution.
        asyncio.Queue is not thread-safe and using an asynchronous function to queue things does not guarantee order.
        Enforces minimum delay between commands.
        Args:
            msg (bytes): Raw bytes to be sent. Usually encoded in ISO-8859-1.
        """
        with self.lock:
            if self.min_spacing:
                time.sleep(max(0, self.min_spacing - (time.monotonic() - self.t_lastcmd)))
            self._serial.writer.write(msg)
            self.t_lastcmd = time.monotonic()
            logger.debug(f"{self.name}Tx: {msg}")

    @staticmethod
    async def async_wrapper(fut):
        return await fut
