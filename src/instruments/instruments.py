from typing import Callable, ClassVar, Protocol, Tuple

from src.utils.com import COM, Command


class Instruments(Protocol):
    COMMANDS: ClassVar[Command]
    SERIAL_FORMATTER: ClassVar[Callable[[str], str]]
    com: COM

    def initialize(self) -> None:
        ...

    def send(self, msg: str) -> str:
        ...

    @staticmethod
    def _serial_formatter(s: str) -> str:
        ...


class Movable(Instruments):
    STEPS_PER_UM: ClassVar[float]
    RANGE: ClassVar[Tuple[int, int]]
    HOME: ClassVar[int]

    @property
    def position(self) -> int:
        ...

    @position.setter
    def position(self, p: int) -> None:
        ...
