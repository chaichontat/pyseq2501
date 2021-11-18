from __future__ import annotations

import io
from dataclasses import dataclass
from enum import Enum, unique
from logging import Logger
from typing import Optional

import serial

# @dataclass(frozen=True)
# class CmdNoArg:
#     cmd: str
#     verify: Optional[Callable[[str], bool]] = None


# @dataclass(frozen=True)
# class CmdWithArg:
#     cmd: Callable[[str], str]
#     verify: Optional[Callable[[str, str], bool]] = None


# class InvalidResponse(Exception):
#     ...


@unique
class Command(Enum):
    def __str__(self) -> str:
        return self.value


@dataclass
class COM:
    port: str
    baud: int
    logger: Optional[Logger] = None
    timeout: int = 1
    prefix: str = ""
    suffix: str = ""

    def __post_init__(self) -> None:
        s = serial.Serial(self.port, self.baud, timeout=self.timeout)
        # Text wrapper around serial port
        self.sp = io.TextIOWrapper(io.BufferedRWPair(s, s), encoding="ascii", errors="strict")  # type: ignore[arg-type]

    def send(self, cmd: str | Command) -> str:
        cmd = str(cmd)
        self.sp.write(self.prefix + cmd + self.suffix)
        self.sp.flush()
        resp = self.sp.readline().strip()
        if self.logger is not None:
            self.logger.debug(f"Tx: {cmd:10} Rx: {resp:10}")
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
