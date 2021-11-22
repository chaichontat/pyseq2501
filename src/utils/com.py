from __future__ import annotations

import io
import threading
from concurrent.futures import Future, ThreadPoolExecutor
from dataclasses import dataclass, field
from enum import Enum, unique
from functools import wraps
from logging import Logger
from typing import Callable, Optional, TypeVar, Union, cast, overload

from serial import Serial

try:
    profile  # type: ignore[has-type]
except NameError:
    profile = lambda f: f

# @dataclass(frozen=True)
# class CmdWithArg:
#     cmd: Callable[[str], str]
#     verify: Optional[Callable[[str, str], bool]] = None


@unique
class Command(Enum):
    def __str__(self) -> str:
        return self.value


T = TypeVar("T", bound=Callable[..., str])


def is_between(f: T, min_: int, max_: int) -> T:
    @wraps
    def wrapper(x: int) -> str:
        if not (min_ <= x <= max_) or x != int(x):
            raise ValueError(f"Invalid value for {f.__name__}: Got {x}. Expected [{min_}, {max_}].")
        return f(x)

    return cast(T, wrapper)


Str2Bool = Callable[[str], bool]
StrCmd = Union[str, Command]


@dataclass
class CmdVerify:
    cmd: str | Command
    expected: Callable[[str], str]


class InvalidResponse(Exception):
    def __init__(self, tx: StrCmd, rx: str):
        self.tx = tx
        self.rx = rx


class SerialWriteFailed(Exception):
    ...


# TERRIBLE HORRIBLE NO GOOD VERY BAD HACK
# TODO: Wait for Python 3.10 and use PEP-612 ParamSpec.

A = TypeVar("A")
B = TypeVar("B")
C = TypeVar("C")
S = TypeVar("S")
Z = TypeVar("Z")


@overload
def run_in_executor(f: Callable[[A], Z]) -> Callable[[A], Future[Z]]:
    ...


@overload
def run_in_executor(f: Callable[[A, B], Z]) -> Callable[[A, B], Future[Z]]:
    ...


@overload
def run_in_executor(f: Callable[[A, B, C], Z]) -> Callable[[A, B, C], Future[Z]]:
    ...


def run_in_executor(f: Callable[..., Z]) -> Callable[..., Future[Z]]:
    """
    Prevents a race condition in which a result from the running object is dependent on an object in the queue.
    """

    @wraps(f)
    def inner(self: COM, *args, **kwargs) -> Future:
        if threading.current_thread() not in self._executor._threads:  # type: ignore[attr-defined]
            return self._executor.submit(lambda: f(self, *args, **kwargs))
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

    @run_in_executor
    def put(self, f: Callable[[], S]) -> S:
        return f()

    def _send_for_thread(self, cmd: StrCmd) -> None:
        assert self.formatter is not None
        self._serial.write(self.formatter(str(cmd)))

    @run_in_executor
    def send(self, cmd: StrCmd) -> None:
        self._send_for_thread(cmd)
        if self.logger is not None:
            self.logger.debug(f"Tx: {cmd:10}")

    def _repl_for_thread(self, cmd: StrCmd) -> str:
        self._send_for_thread(cmd)
        self._serial.flush()
        return self._serial.readline().strip()

    @run_in_executor
    def repl(self, cmd: StrCmd) -> str:
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
