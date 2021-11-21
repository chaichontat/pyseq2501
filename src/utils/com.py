from __future__ import annotations

import io
from concurrent.futures import Future, ThreadPoolExecutor, as_completed, wait
from contextlib import contextmanager
from dataclasses import dataclass, field
from enum import Enum, unique
from logging import Logger
from typing import Any, Callable, Final, Optional, Union

from serial import Serial

# from exceptions import InvalidResponse

# @dataclass(frozen=True)
# class CmdNoArg:
#     cmd: str
#     verify: Optional[Callable[[str], bool]] = None

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


Str2Bool = Callable[[str], bool]
StrCmd = Union[str, Command]


@dataclass
class CmdVerify:
    cmd: str | Command
    expected: Callable[[str], str]


class InvalidResponse(Exception):
    def __init__(self, tx: str | Command, rx: str):
        self.tx = tx
        self.rx = rx


class SerialWriteFailed(Exception):
    ...


class COMJob:
    def __init__(self, f: Callable[[], Optional[str]], waiting: bool = False) -> None:
        self.f: Final = f
        self.waiting: Final = waiting


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
        # Text wrapper around serial port
        self._serial = io.TextIOWrapper(io.BufferedRWPair(s_tx, s_rx), encoding="ascii", errors="strict")  # type: ignore[arg-type]
        self._executor = ThreadPoolExecutor(max_workers=1)

    def put_job(self, f: Callable[[], Any]) -> None:
        self._executor.submit(f)

    def _send_for_thread(self, cmd: StrCmd) -> None:
        assert self.formatter is not None
        self._serial.write(self.formatter(str(cmd)))

    def send(self, cmd: StrCmd) -> Future[None]:
        def work() -> None:
            self._send_for_thread(cmd)
            if self.logger is not None:
                self.logger.debug(f"Tx: {cmd:10}")

        return self._executor.submit(work)

    def send_blocking(self, cmd: StrCmd) -> None:
        future = self.send(cmd)
        future.result()

    def _repl_for_thread(self, cmd: StrCmd) -> str:
        self._send_for_thread(cmd)
        self._serial.flush()
        return self._serial.readline().strip()

    def repl(self, cmd: str | Command) -> Future[str]:
        def work() -> str:
            resp = self._repl_for_thread(cmd)
            if self.logger is not None:
                self.logger.debug(f"Tx: {cmd:10} Rx: {resp:10}")
            return resp

        return self._executor.submit(work)

    def join(self) -> None:
        self._executor.submit(lambda: None).result()

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

    #     self._q_tx.put(Job(work, waiting))

    # @overload
    # def send(self, cmd: CmdNoArg, arg: None, rep: int) -> str:
    #     ...

    # @overload
    # def send(self, cmd: CmdWithArg, arg: str, rep: int) -> str:
    #     ...

    # def send(self, cmd: CmdNoArg | CmdWithArg, arg: None | str, rep: int = 10) -> str:
    #     if isinstance(cmd, CmdNoArg):
    #         to_send = cmd.cmd
    #     elif isinstance(cmd, CmdWithArg):
    #         # See https://github.com/python/mypy/issues/5485
    #         to_send = cmd.cmd(arg)  # type:ignore[misc,operator]
    #     else:
    #         raise TypeError

    #     self.sp.write(self.prefix + to_send + self.suffix)  # Write to serial port
    #     self.sp.flush()  # Flush serial port
    #     resp = self.sp.readline()

    #     if cmd.verify is not None:
    #         for _ in range(rep):
    #             if isinstance(cmd, CmdNoArg):
    #                 if cmd.verify(resp):
    #                     break

    #             elif isinstance(cmd, CmdWithArg):
    #                 assert arg is not None
    #                 if cmd.verify(resp, arg):
    #                     break
    #         else:
    #             raise InvalidResponse

    #     if self.logger is not None:
    #         self.logger.debug(f"Tx: {arg:10} Rx: {resp:10}")
    #     return resp
