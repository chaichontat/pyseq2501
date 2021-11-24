import io
import os
import time
from concurrent.futures import ThreadPoolExecutor
from dataclasses import dataclass, field
from logging import Logger
from typing import Callable, Generic, Optional, TypeVar, cast, overload

from returns.pipeline import is_successful
from returns.result import Result
from serial import Serial
from src.instruments_types import SerialInstruments

from .fakeserial import FakeSerial
from .utils import FakeLogger, run_in_executor

ReturnsStr = TypeVar("ReturnsStr", bound=Callable[..., str])
T = TypeVar("T")
F = TypeVar("F")


def is_between(f: ReturnsStr, min_: int, max_: int) -> ReturnsStr:
    def wrapper(x: int) -> str:
        if not (min_ <= x <= max_) or x != int(x):
            raise ValueError(f"Invalid value for {f.__name__}: Got {x}. Expected [{min_}, {max_}].")
        return f(x)

    return cast(ReturnsStr, wrapper)


@dataclass(frozen=True)
class CmdParse(Generic[T, F]):
    cmd: str | Callable[[str], str]
    process: Callable[[str], Result[T, F]]

    def __call__(self: T, arg: str) -> T:
        return CmdParse(self.cmd(arg), self.process)  # type: ignore

    def __str__(self) -> str:
        return str(self.cmd)


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
    logger: Logger | FakeLogger = FakeLogger()
    timeout: int = 1
    _formatter: Formatter = field(init=False)
    _executor: ThreadPoolExecutor = field(init=False)

    def __post_init__(self) -> None:
        self.formatter = SERIAL_FORMATTER[self.name]
        try:
            use_fake = os.environ["FAKE_HISEQ"] == "1"
        except KeyError:
            use_fake = False

        if use_fake:
            self._serial = FakeSerial(self.name, self.port_tx, self.port_rx, self.timeout)
        else:
            s_tx = Serial(self.port_tx, BAUD_RATE[self.name], timeout=self.timeout)
            s_rx = s_tx or Serial(self.port_rx, BAUD_RATE[self.name], timeout=self.timeout)
            self._serial = io.TextIOWrapper(io.BufferedRWPair(s_tx, s_rx), encoding="ascii", errors="strict")  # type: ignore[arg-type]

        self._executor = ThreadPoolExecutor(max_workers=1)

    @run_in_executor
    def put(self, f: Callable[[], T]) -> T:
        return f()

    def _send_for_thread(self, cmd: str) -> None:
        assert self.formatter is not None
        self._serial.write(self.formatter(cmd))

    def _send(self, cmd: str) -> None:
        self._send_for_thread(cmd)
        self.logger.debug(f"Tx: {cmd:10}")

    @run_in_executor
    def send(self, cmd: str) -> None:
        return self._send(cmd)

    def _repl_for_thread(self, cmd: str) -> str:
        self._send_for_thread(cmd)
        self._serial.flush()
        return self._serial.readline().strip()

    @overload
    def _repl(self, cmd: str) -> str:
        ...

    @overload
    def _repl(self, cmd: CmdParse[T, F]) -> T:
        ...

    def _repl(self, cmd: str | CmdParse[T, F]) -> str | T:
        if isinstance(cmd, CmdParse):
            if isinstance(x := cmd.cmd, str):
                send = x
            else:
                raise TypeError("This command requires an argument, call this command first.")

            raw = self._repl_for_thread(send)
            resp = cmd.process(raw)
            if is_successful(resp):
                self.logger.debug(f"Tx: {send:10} Rx: {raw:10} [green]Verified")
            else:
                self.logger.warning(f"Verification failed for {send}. Got {resp.failure()}. Expected {send}.")
            return resp.unwrap()

        else:
            resp = self._repl_for_thread(cmd)
            self.logger.debug(f"Tx: {cmd:10} Rx: {resp:10}")
            return resp

    @overload
    @run_in_executor
    def repl(self, cmd: str) -> str:
        ...

    @overload
    @run_in_executor
    def repl(self, cmd: str, checker: Callable[[str], bool], *, attempts: int) -> str:
        ...

    @overload
    @run_in_executor
    def repl(self, cmd: CmdParse[T, F]) -> T:
        ...

    @overload
    @run_in_executor
    def repl(self, cmd: CmdParse[T, F], checker: Callable[[T], bool], *, attempts: int) -> T:
        ...

    @run_in_executor
    def repl(
        self, cmd: str | CmdParse[T, F], checker: Callable[[T], bool] = lambda _: True, *, attempts: int = 2
    ) -> str | T:
        if attempts < 1:
            raise ValueError("Attempts must be >= 1.")

        temp = ""
        for _ in range(attempts):
            if checker(resp := self._repl(cmd)):
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
