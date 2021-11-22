import io
import threading
from concurrent.futures import Future, ThreadPoolExecutor
from dataclasses import dataclass, field
from functools import wraps
from logging import Logger
from typing import Any, Callable, Optional, ParamSpec, TypeVar, cast

from serial import Serial


@dataclass(frozen=True)
class CmdVerify:
    cmd: str
    expected: Callable[[str], str]


T = TypeVar("T", bound=Callable[..., str])


def is_between(f: T, min_: int, max_: int) -> T:
    def wrapper(x: int) -> str:
        if not (min_ <= x <= max_) or x != int(x):
            raise ValueError(f"Invalid value for {f.__name__}: Got {x}. Expected [{min_}, {max_}].")
        return f(x)

    return cast(T, wrapper)


Str2Bool = Callable[[str], bool]


class InvalidResponse(Exception):
    def __init__(self, tx: str, rx: str):
        self.tx = tx
        self.rx = rx


class SerialWriteFailed(Exception):
    ...


P = ParamSpec("P")
Z = TypeVar("Z")

# Wait until mypy supports ParamSpec.
def run_in_executor(f: Callable[P, Z]) -> Callable[P, Future[Z]]:  # type: ignore[misc]
    """
    Prevents a race condition in which a result from the running object is dependent on an object in the queue.
    """

    @wraps(f)
    def inner(self: COM, *args: Any, **kwargs: Any) -> Future[Z]:
        if threading.current_thread() not in self._executor._threads:  # type: ignore[attr-defined]
            return cast(Future[Z], self._executor.submit(lambda: f(self, *args, **kwargs)))
        else:
            future: Future[Z] = Future()
            future.set_result(f(self, *args, **kwargs))
            return future

    return inner


@dataclass
class COM:
    baud: int
    port_tx: str
    port_rx: Optional[str] = None
    logger: Optional[Logger] = None
    formatter: Optional[Callable[[str], str]] = None
    timeout: int = 1
    _executor: ThreadPoolExecutor = field(init=False)

    def __post_init__(self) -> None:
        if self.formatter is None:
            self.formatter = lambda x: x

        s_tx = Serial(self.port_tx, self.baud, timeout=self.timeout)
        s_rx = s_tx if self.port_rx is None else Serial(self.port_rx, self.baud, timeout=self.timeout)
        self._serial = io.TextIOWrapper(io.BufferedRWPair(s_tx, s_rx), encoding="ascii", errors="strict")  # type: ignore[arg-type]
        self._executor = ThreadPoolExecutor(max_workers=1)

    S = TypeVar("S")

    @run_in_executor
    def put(self, f: Callable[[], S]) -> S:
        return f()

    def _send_for_thread(self, cmd: str) -> None:
        assert self.formatter is not None
        self._serial.write(self.formatter(cmd))

    @run_in_executor
    def send(self, cmd: str) -> None:
        self._send_for_thread(cmd)
        if self.logger is not None:
            self.logger.debug(f"Tx: {cmd:10}")

    def _repl_for_thread(self, cmd: str) -> str:
        self._send_for_thread(cmd)
        self._serial.flush()
        return self._serial.readline().strip()

    @run_in_executor
    def repl(self, cmd: str) -> str:
        resp = self._repl_for_thread(cmd)
        if self.logger is not None:
            self.logger.debug(f"Tx: {cmd:10} Rx: {resp:10}")
        return resp

    @run_in_executor
    def is_done(self) -> None:
        return None

    # def repl_verify(self, cmdver: CmdVerify, waiting: bool = False, attempts: int = 2) -> str:
    #     def work() -> str:
    #         expected = cmdver.expected(str(cmdver.cmd))
    #         for _ in range(attempts):
    #             resp = self._repl_for_thread(cmdver.cmd)
    #             if resp == expected:
    #                 break
    #             if self.logger is not None:
    #                 self.logger.debug(f"Verification failed for {cmdver.cmd}. Expected {expected} Got {resp}.")
    #         else:
    #             raise InvalidResponse(cmdver.cmd, resp)
    #         return resp
