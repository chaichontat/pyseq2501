from __future__ import annotations

import io
from contextlib import contextmanager
from dataclasses import dataclass, field
from enum import Enum, unique
from logging import Logger
from queue import Queue
from threading import Thread
from typing import Any, Callable, Final, NoReturn, Optional, Union

# from concurrent.futures import ThreadPoolExecutor
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
    thread: Thread = field(init=False)
    _q_tx: Queue[COMJob | Callable[[], Any]] = field(init=False)
    _q_rx: Queue[str] = field(init=False)
    _executor: ThreadPoolExecutor = field(init=False)

    def __post_init__(self) -> None:
        if self.formatter is None:
            self.formatter = lambda x: x

        s_tx = Serial(self.port_tx, self.baud, timeout=self.timeout)
        s_rx = s_tx if self.port_rx is None else Serial(self.port_rx, self.baud, timeout=self.timeout)
        # Text wrapper around serial port
        self._serial = io.TextIOWrapper(io.BufferedRWPair(s_tx, s_rx), encoding="ascii", errors="strict")  # type: ignore[arg-type]

        self._q_tx = Queue()
        self._q_rx = Queue(maxsize=1)  # Block if waiting for a response.

        # self._executor = ThreadPoolExecutor(max_workers=1)

        def worker(self) -> NoReturn:
            while True:
                f = self._q_tx.get()
                if isinstance(f, COMJob):
                    if (resp := f.f()) is not None and f.waiting:
                        self._q_rx.put(resp)
                elif callable(f):
                    f()
                else:
                    raise TypeError("Invalid command sent to thread.")
                self._q_tx.task_done()

        self._thread = Thread(target=worker, args=(self,), daemon=True)
        self._thread.start()

    def put_job(self, f: Callable[[], Any]) -> None:
        self._q_tx.put(f)

    def _send_for_thread(self, cmd: StrCmd) -> None:
        assert self.formatter is not None
        self._serial.write(self.formatter(str(cmd)))

    def send(self, cmd: StrCmd) -> None:
        def work() -> None:
            self._send_for_thread(cmd)
            if self.logger is not None:
                self.logger.debug(f"Tx: {cmd:10}")

        self._q_tx.put(COMJob(work))

    def send_blocking(self, cmd: StrCmd) -> None:
        self.send(cmd)
        self._q_tx.join()

    def _repl_for_thread(self, cmd: StrCmd) -> str:
        self._send_for_thread(cmd)
        self._serial.flush()
        return self._serial.readline().strip()

    def repl(self, cmd: str | Command, waiting: bool = False) -> Optional[str]:
        def work() -> str:
            resp = self._repl_for_thread(cmd)
            if self.logger is not None:
                self.logger.debug(f"Tx: {cmd:10} Rx: {resp:10}")
            return resp

        self._q_tx.put(COMJob(work, waiting))
        if waiting:
            # self._q_tx.join()  # Shouldn't be necessary but just in case.
            return self._q_rx.get()
        return None

    def join(self) -> None:
        self._q_tx.join()

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
