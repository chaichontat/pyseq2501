from concurrent.futures import Future
from typing import Callable, ClassVar, Protocol, Tuple

from src.utils.com import COM, Command


class UsesSerial(Protocol):
    COMMANDS: ClassVar[Command]
    SERIAL_FORMATTER: ClassVar[Callable[[str], str]]
    com: COM

    def initialize(self) -> Future:
        ...

    @staticmethod
    def _serial_formatter(s: str) -> str:
        ...


class Movable(UsesSerial):
    STEPS_PER_UM: ClassVar[float]
    RANGE: ClassVar[Tuple[int, int]]
    HOME: ClassVar[int]

    @property
    def position(self) -> Future[int]:
        ...
