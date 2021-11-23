import io
import os
import threading
from concurrent.futures import Executor, Future, ThreadPoolExecutor
from dataclasses import dataclass, field
from functools import wraps
from logging import Logger
from typing import Any, Callable, Optional, ParamSpec, Protocol, TypeVar, cast

from returns.pipeline import is_successful
from returns.result import Failure, Result, Success
from serial import Serial
from src.instruments_types import SerialInstruments

from .fakeserial import FakeSerial
from .utils import FakeLogger

T = TypeVar("T", bound=Callable[..., str])


def is_between(f: T, min_: int, max_: int) -> T:
    def wrapper(x: int) -> str:
        if not (min_ <= x <= max_) or x != int(x):
            raise ValueError(f"Invalid value for {f.__name__}: Got {x}. Expected [{min_}, {max_}].")
        return f(x)

    return cast(T, wrapper)


P = ParamSpec("P")
Z = TypeVar("Z")


class Threaded(Protocol):
    _executor: Executor


# TODO Wait until mypy supports ParamSpec.
def run_in_executor(f: Callable[P, Z]) -> Callable[P, Future[Z]]:  # type: ignore[misc]
    """
    Prevents a race condition in which a result from the running object is dependent on an object in the queue.
    """

    @wraps(f)
    def inner(self: Threaded, *args: Any, **kwargs: Any) -> Future[Z]:
        if threading.current_thread() not in self._executor._threads:  # type: ignore[attr-defined]
            return cast(Future[Z], self._executor.submit(lambda: f(self, *args, **kwargs)))
        else:
            future: Future[Z] = Future()
            future.set_result(f(self, *args, **kwargs))
            return future

    return inner


@dataclass(frozen=True)
class CmdVerify:
    cmd: str | Callable[[str], str]
    process: Callable[[str], Result[Any, Any]]


Formatter = Callable[[str], str]
BAUD_RATE: dict[SerialInstruments, int] = dict(fpga=115200, x=9600, y=9600, laser_g=9600, laser_r=9600)
# fmt:off
SERIAL_FORMATTER: dict[SerialInstruments, Callable[[str], str]] = dict(
       fpga=lambda x:  f"{x}\n",
          x=lambda x:  f"{x}\r",
          y=lambda x: f"1{x}\r\n",
    laser_g=lambda x:  f"{x}\r",
    laser_r=lambda x:  f"{x}\r",
)
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
            self._serial = FakeSerial(self.port_tx, self.port_rx, self.timeout)
        else:
            s_tx = Serial(self.port_tx, BAUD_RATE[self.name], timeout=self.timeout)
            s_rx = s_tx or Serial(self.port_rx, BAUD_RATE[self.name], timeout=self.timeout)
            self._serial = io.TextIOWrapper(io.BufferedRWPair(s_tx, s_rx), encoding="ascii", errors="strict")  # type: ignore[arg-type]

        self._executor = ThreadPoolExecutor(max_workers=1)

    S = TypeVar("S")

    @run_in_executor
    def put(self, f: Callable[[], S]) -> S:
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

    def _repl(self, cmd: str) -> str:
        resp = self._repl_for_thread(cmd)
        self.logger.debug(f"Tx: {cmd:10} Rx: {resp:10}")
        return resp

    @run_in_executor
    def repl(self, cmd: str) -> str:
        return self._repl(cmd)

    def _repl_verify(self, cmdver: CmdVerify, arg: Optional[str] = None, attempts: int = 2) -> Any:

        assert attempts > 0
        if isinstance(x := cmdver.cmd, str):
            send = x
        elif arg is None:
            raise TypeError("Command needs argument but argument is None.")
        else:
            send = x(arg)

        resp: Result[Any, Any]
        for i in range(attempts):
            raw = self._repl_for_thread(send)
            resp = cmdver.process(raw)  # type: ignore[misc,operator]
            if is_successful(resp):
                self.logger.debug(f"Tx: {send:10} Rx: {raw:10} [green]Verified")
                break
            self.logger.warning(f"Verification failed for {send}. Got {resp.failure()}. Attempt {i}")
        else:
            self.logger.error(f"Verification failed for {send}. Max attempts reached.")
        return resp.unwrap()

    @run_in_executor
    def repl_verify(self, cmdver: CmdVerify, arg: Optional[str] = None, attempts: int = 2) -> Any:
        return self._repl_verify(cmdver, arg, attempts)

    @run_in_executor
    def is_done(self) -> None:
        return None
