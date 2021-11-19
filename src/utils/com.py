from __future__ import annotations

import io
from dataclasses import dataclass
from enum import Enum, unique
from logging import Logger
from typing import Callable, Optional

from serial import Serial

# from exceptions import InvalidResponse

# @dataclass(frozen=True)
# class CmdNoArg:
#     cmd: str
#     verify: Optional[Callable[[str], bool]] = None


# @dataclass(frozen=True)
# class CmdWithArg:
#     cmd: Callable[[str], str]
#     verify: Optional[Callable[[str, str], bool]] = None

Str2Bool = Callable[[str], bool]


@unique
class Command(Enum):
    def __str__(self) -> str:
        return self.value


@dataclass
class CmdVerify:
    cmd: str | Command
    verify: Callable[[str, str], bool]


class InvalidResponse(Exception):
    def __init__(self, tx: str | Command, rx: str):
        self.tx = tx
        self.rx = rx


@dataclass
class COM:
    baud: int
    port_tx: str
    port_rx: Optional[str] = None
    logger: Optional[Logger] = None
    formatter: Callable[[COM, str], str] = lambda _, x: x
    timeout: int = 1

    def __post_init__(self) -> None:
        s_tx = Serial(self.port_tx, self.baud, timeout=self.timeout)
        s_rx = s_tx if self.port_rx is None else Serial(self.port_rx, self.baud, timeout=self.timeout)
        # Text wrapper around serial port
        self.serial = io.TextIOWrapper(io.BufferedRWPair(s_tx, s_rx), encoding="ascii", errors="strict")  # type: ignore[arg-type]

    def send(self, cmd: str | Command) -> None:
        self.serial.write(self.formatter(str(cmd)))

    def repl(self, cmd: str | Command) -> str:
        self.send(cmd)
        self.serial.flush()
        resp = self.serial.readline().strip()
        if self.logger is not None:
            if isinstance(cmd, Command):
                cmd = cmd.name
            self.logger.debug(f"Tx: {cmd:10} Rx: {resp:10}")
        return resp

    def repl_verify(self, cmdver: CmdVerify, attempts: int = 2) -> str:
        for _ in range(attempts):
            resp = self.repl(cmdver.cmd)
            if cmdver.verify(resp, str(cmdver.cmd)):
                break
        else:
            raise InvalidResponse(cmdver.cmd, resp)
        return resp

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
