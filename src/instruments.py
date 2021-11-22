from __future__ import annotations

from concurrent.futures import Future
from logging import Logger
from typing import Callable, ClassVar, Optional, Protocol, Tuple

from src.utils.com import COM, Command


class UsesSerial(Protocol):
    BAUD_RATE: ClassVar[int]
    CMDS: ClassVar[Command]
    SERIAL_FORMATTER: ClassVar[Callable[[str], str]]
    com: COM

    def __init__(self, port_tx: str, port_rx: Optional[str] = None, logger: Optional[Logger] = None) -> None:
        super().__init__()
        self.com = COM(self.BAUD_RATE, port_tx, port_rx, logger=logger, formatter=self.SERIAL_FORMATTER)

    def initialize(self) -> Future:
        raise NotImplementedError

    @staticmethod
    def _serial_formatter(s: str) -> str:
        ...


class Movable(Protocol):
    STEPS_PER_UM: ClassVar[int | float]
    RANGE: ClassVar[Tuple[int, int]]
    HOME: ClassVar[int]

    @property
    def position(self) -> Future[int]:
        raise NotImplementedError


class FPGAControlled(Protocol):
    fpga_com: COM

    def __init__(self, fpga_com: COM) -> None:
        super().__init__()
        self.fpga_com = fpga_com
