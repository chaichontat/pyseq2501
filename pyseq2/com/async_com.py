from __future__ import annotations

import asyncio
import logging
import time
from asyncio import Future, StreamReader, StreamWriter
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

from pyseq2.base.instruments_types import SerialInstruments
from pyseq2.utils.utils import InvalidResponse
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
        **This is usually true except for `move` commands in which the instrument is
          programmed to respond on completion**

    - All responses are accounted for.

    Specific to each COM channel.

    Args:
        name (SerialInstruments): Name of the instrument.
        port_tx (str): COM port.
        port_rx (Optional[str], optional): Receiving port if different from port_tx.
            Only the FPGA uses separate channels.
        min_spacing (int, optional): Minimum time between commands. Defaults to 0.05s.
        no_check (bool, optional): Do not check for return values. Defaults to False.
    """

    @classmethod
    async def ainit(
        cls,
        name: SerialInstruments,
        port_tx: str,
        port_rx: Optional[str] = None,
        min_spacing: Annotated[int | float, "s"] = 0.01,
        no_check: bool = False,
    ):

        self = cls(name, min_spacing, no_check)
        if port_rx is not None:
            assert name == "fpga"
            srx = await open_serial_connection(url=port_rx, baudrate=115200)
            stx = await open_serial_connection(url=port_tx, baudrate=115200)
            self._serial = Channel(reader=srx[0], writer=stx[1])
            logger.info(f"{self.name}Started listening to ports {port_tx} and {port_rx}.")
        else:
            assert name != "fpga"
            self._serial = Channel(*await open_serial_connection(url=port_tx, baudrate=9600))
            logger.info(f"{self.name}Started listening to port {port_tx}.")

        asyncio.create_task(self._read_forever())
        return self

    def __init__(
        self,
        name: SerialInstruments,
        min_spacing: Annotated[int | float, "s"] = 0.05,
        no_check: bool = False,
    ) -> None:

        self.name = f"[{COLOR[name]}]{name:10s}[/{COLOR[name]}]"
        self.formatter = FORMATTER[name]
        self.no_check = no_check

        self.min_spacing = min_spacing
        self.t_lastcmd = time.monotonic()
        self.lock = asyncio.Lock()

        self._read_queue: asyncio.Queue[tuple[CmdParse[Any, Any], asyncio.Future[Any]]] = asyncio.Queue()
        self._serial: Channel

        self.waiting = None

    async def _read_forever(self) -> NoReturn:
        while True:
            print(time.time(), "waiting")
            resp = (await self._serial.reader.readline()).decode(**ENCODING_KW).strip()

            if self.no_check:
                logger.debug(resp)
                continue

            if not resp:  # len == 0
                continue

            # For commands that can return later.
            if self.waiting is not None:
                try:
                    parsed = self.waiting[0](resp)
                except InvalidResponse as e:
                    ...
                else:
                    logger.debug(f"{self.name}Rx: Waited {resp:20s} [green]Parsed: '{parsed}'")
                    self.waiting[1].set_result(parsed)
                    self.waiting = None
                    continue

            try:
                cmd, fut = self._read_queue.get_nowait()
            except asyncio.QueueEmpty:
                logger.warning(f"{self.name}Got mysterious return '{resp}'.")
                continue

            try:
                for _ in range(1, cmd.n_lines):
                    print(f"{time.time()} multiline")
                    resp += "\n" + (await self._serial.reader.readline()).decode(**ENCODING_KW).strip()
                parsed = cmd.parser(resp)
            except BaseException as e:
                logger.error(f"{self.name}Exception {str(e)} while parsing '{resp}' from '{cmd.cmd}'.")
                fut.set_exception(e)
            else:
                r = "'" + resp.replace("\n", "\\n") + "'"
                logger.debug(f"{self.name}Rx:  {r:20s} [green]Parsed: '{parsed}'")
                fut.set_result(parsed)
            finally:
                self._read_queue.task_done()

    @overload
    async def send(self, msg: str) -> None:
        ...

    @overload
    async def send(self, msg: CmdParse[T, Any]) -> T:
        ...

    async def send(self, msg: str | CmdParse[T, Any], option=None) -> None | T:
        """Sends a command to an instrument.
        If msg is string   => no responses expected.
        If msg is CmdParse => response expected and parsed by CmdParse.parser.
            Unexpected response triggers a warning and returns Future[None].

        If msg is a list of either above, map this function to all elements.

        wait_next_cmd: bool = False. Current command can return _after_ the next command.
            Solution is to block the execution of the next command until this command is returned.

        Returns:
            None for msg, Future of a CmdParse result.
        """

        if isinstance(msg, str):
            await self._send(self.formatter(msg).encode(**ENCODING_KW))
            return None

        if not isinstance(msg.cmd, str):
            raise ValueError("This command needs argument(s), call it first.")

        fut: Future[T] = asyncio.Future()

        # Need lock as reversal can happen when two closely spaced commands enter.
        # While the former is waiting for min_spacing, the later could arrive just a
        # little later to pass the min_spacing check without waiting.
        async with self.lock:
            if option:
                if self.waiting is not None:
                    raise Exception("Cannot have >1 delayable commands at a time.")
                self.waiting = (option, fut)
                self._read_queue.put_nowait((msg, asyncio.Future()))  # Dump future
            else:
                self._read_queue.put_nowait((msg, fut))

            await self._send(self.formatter(msg.cmd).encode(**ENCODING_KW))

        return await fut

    async def _send(self, msg: bytes) -> None:
        """This needs to be synchronous to maintain order of execution.
        asyncio.Queue is not thread-safe and using an asynchronous function to queue things does not guarantee order.
        Enforces minimum delay between commands.
        Args:
            msg (bytes): Raw bytes to be sent. Usually encoded in ISO-8859-1.
        """
        if self.min_spacing:
            await asyncio.sleep(max(0, self.min_spacing - (time.monotonic() - self.t_lastcmd)))
        self._serial.writer.write(msg)
        self.t_lastcmd = time.monotonic()
        logger.debug(f"{self.name}Tx: {msg}")

    async def wait(self) -> None:
        return await self._read_queue.join()


async def interactive():
    import aioconsole
    from pyseq2.utils.ports import get_ports
    from rich.logging import RichHandler

    logging.basicConfig(
        level="NOTSET",
        format="[yellow]%(name)-10s[/] %(message)s",
        datefmt="[%X]",
        handlers=[RichHandler(rich_tracebacks=True, markup=True)],
    )

    name: SerialInstruments = await aioconsole.ainput("Instrument? ")
    com = await COM.ainit(name, getattr(get_ports(), name))
    while True:
        await asyncio.sleep(0.2)
        line = await aioconsole.ainput("Command? ")
        await aioconsole.aprint()
        await com.send(line)


if __name__ == "__main__":
    asyncio.run(interactive())
