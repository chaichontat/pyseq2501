from __future__ import annotations

import io
import os
import time
from concurrent.futures import ThreadPoolExecutor
from dataclasses import dataclass, field
from logging import Logger, getLogger
from typing import IO, Any, Callable, Generic, Optional, ParamSpec, TypeVar, Union, cast, overload

from serial import Serial
from src.base.instruments_types import SerialInstruments

from .fakeserial import FakeSerial
from .utils import run_in_executor

ReturnsStr = TypeVar("ReturnsStr", bound=Callable[..., str])
T = TypeVar("T")
F = TypeVar("F")
P = ParamSpec("P")
flint = int | float


def is_between(f: ReturnsStr, min_: int, max_: int) -> ReturnsStr:
    def wrapper(x: int) -> str:
        if not (min_ <= x <= max_) or x != int(x):
            raise ValueError(f"Invalid value for {f.__name__}: Got {x}. Expected [{min_}, {max_}].")
        return f(x)

    return cast(ReturnsStr, wrapper)


S = TypeVar("S", bound=Union[Callable[..., str], str])


@dataclass(frozen=True)
class CmdParse(Generic[T]):
    """A command with its parsing function.

    Args:
        cmd: String command or a unary function that outputs a command.
        process: A unary function that takes in raw output from the device and parse it into a useful format.
            Uses the Result architecture.

    Returns:
        A data structure where a command and its parsing function are together.
    """

    cmd: str | Callable[..., str]
    parser: Callable[[str], T]

    def __call__(self, *args: ..., **kwargs: ...) -> CmdParse[T]:
        if isinstance(self.cmd, str):
            raise TypeError("This command does not take argument(s).")
        return CmdParse(self.cmd(*args, **kwargs), self.parser)

    def __str__(self) -> str:
        return str(self.cmd)


def ok_if_match(target: list[str] | str) -> Callable[[str], bool]:
    def wrapped(resp: str) -> bool:
        if isinstance(target, list):
            return True if resp in target else False
        else:
            return True if resp == target else False

    return wrapped


Formatter = Callable[[str], str]
BAUD_RATE: dict[SerialInstruments, int] = dict(fpga=115200, x=9600, y=9600, laser_g=9600, laser_r=9600)  # type: ignore
# fmt:off
SERIAL_FORMATTER: dict[SerialInstruments, Callable[[str], str]] = dict(
       fpga=lambda x:  f"{x}\n",
    laser_g=lambda x:  f"{x}\r",
    laser_r=lambda x:  f"{x}\r",
          x=lambda x:  f"{x}\r",
          y=lambda x: f"1{x}\r\n",
)  # type: ignore
# fmt:on


@dataclass
class COM:
    name: SerialInstruments
    port_tx: str
    port_rx: Optional[str] = None
    timeout: Optional[int | float] = 1
    logger: Logger = field(init=False)
    _formatter: Formatter = field(init=False)
    _executor: ThreadPoolExecutor = field(init=False)

    """
    Serial communication middleman. Each port is designed to be run in its own thread.
    Methods prepended with _ executes in the current thread whereas those without would
    run in its own thread.
    """

    def __post_init__(self) -> None:
        self.formatter = SERIAL_FORMATTER[self.name]
        use_fake = os.environ.get("FAKE_HISEQ", "0") == "1" or os.name != "nt"
        self._executor = ThreadPoolExecutor(max_workers=1)
        self.logger = getLogger(f"COM{self.name}")

        if use_fake:
            self._serial = FakeSerial(self.name, self.port_tx, self.port_rx, self.timeout)
            return

        stx = Serial(self.port_tx, BAUD_RATE[self.name], timeout=self.timeout)
        if self.port_rx is not None:
            srx = Serial(self.port_rx, BAUD_RATE[self.name], timeout=self.timeout)
            self._serial = io.TextIOWrapper(cast(IO[bytes], io.BufferedRWPair(srx, stx)))
        else:
            self._serial = io.TextIOWrapper(cast(IO[bytes], stx))

    @run_in_executor
    def put(self, f: Callable[[], T]) -> T:
        return f()

    def _send(self, cmd: str | CmdParse[Any]) -> None:
        if isinstance(cmd, CmdParse):
            if isinstance(x := cmd.cmd, str):
                cmd = x
            else:
                raise TypeError("This command requires an argument, call this command first.")
        self._serial.write(self.formatter(cmd))
        self.logger.debug(f"Tx: {cmd:10}")

    @run_in_executor
    def send(self, cmd: str | list[str]) -> None:
        if isinstance(cmd, list):
            [self._send(c) for c in cmd]
        else:
            self._send(cmd)
        self._serial.flush()

    @overload
    def _repl(self, cmd: str, oneline: bool = ...) -> str:
        ...

    @overload
    def _repl(self, cmd: CmdParse[T], oneline: bool = ...) -> T:
        ...

    @overload
    def _repl(self, cmd: list[str | CmdParse[Any]]) -> list[Any]:
        ...

    def _repl(
        self, cmd: str | CmdParse[T] | list[str | CmdParse[Any]], oneline: bool = True
    ) -> str | T | list[Any]:
        if not isinstance(cmd, list):
            cmd = [cmd]

        for c in cmd:
            self._send(c)
        self._serial.flush()

        out = []
        for c in cmd:
            raw = self._serial.readline().strip() if oneline else "".join(self._serial.readlines())
            if isinstance(c, CmdParse):
                try:
                    resp = c.parser(raw)
                except Exception as e:
                    self.logger.warning(f"Verification failed for {c.cmd}. Got {raw} with {e}.")
                    resp = raw
                else:
                    self.logger.debug(f"Tx: {c.cmd:10} Rx: {raw:10} [green]Verified")
            else:
                self.logger.debug(f"Tx: {c:10} Rx: {raw:10}")
                resp = raw

            if len(cmd) == 1:  # Check if one command.
                return resp
            else:
                out.append(resp)
        return out

    @overload
    @run_in_executor
    def repl(self, cmd: list[str | CmdParse[Any]]) -> list[Any]:
        ...

    @overload
    @run_in_executor
    def repl(
        self, cmd: str, checker: Callable[[str], bool] = ..., *, oneline: bool = ..., attempts: int = ...
    ) -> str:
        ...

    @overload
    @run_in_executor
    def repl(
        self,
        cmd: CmdParse[T],
        checker: Callable[[T], bool] = ...,
        *,
        oneline: bool = ...,
        attempts: int = ...,
    ) -> T:
        ...

    @run_in_executor
    def repl(
        self,
        cmd: str | CmdParse[T] | list[str | CmdParse[Any]],
        checker: Callable[[T], bool] = lambda _: True,
        *,
        oneline: bool = True,
        attempts: int = 1,
    ) -> str | T | list[Any]:
        if attempts < 1:
            raise ValueError("Attempts must be >= 1.")

        if isinstance(cmd, list):
            return self._repl(cmd)

        temp = ""
        for _ in range(attempts):
            if checker(resp := self._repl(cmd, oneline)):
                break
            self.logger.warning(f"{cmd} failed check. Got {resp}.")
            time.sleep(0.5)
            temp = resp  # For Pylance type check.
        else:
            resp = temp
            self.logger.error(f"{cmd} failed check. Giving up after {attempts} attempts.")
        return resp

    @run_in_executor
    def is_done(self) -> None:
        return None

    def readline(self) -> str:
        return self._serial.readline()

    def readlines(self) -> list[str]:
        res = self._serial.readlines()
        return res if isinstance(res, list) else [res]
