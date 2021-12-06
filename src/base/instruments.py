from __future__ import annotations

from abc import ABCMeta, abstractmethod
from concurrent.futures import Future
from typing import Annotated, Any, ClassVar, NoReturn, final

from src.com.async_com import COM


class UsesSerial(metaclass=ABCMeta):
    com: COM

    @property
    def send(self):
        return self.com.send

    @abstractmethod
    def initialize(self) -> Future[Any]:
        ...

    @property
    def _executor(self) -> NoReturn:
        raise AttributeError  # Prevents executor outside COM.


class Movable(metaclass=ABCMeta):
    STEPS_PER_UM: ClassVar[int | float]
    RANGE: ClassVar[tuple[int, int]]
    HOME: ClassVar[int]

    # def __new__(cls) -> Movable:
    #     (cls.STEPS_PER_UM, cls.RANGE, cls.HOME)  # Check if all classvars are defined.
    #     return super().__new__(cls)

    @abstractmethod
    def move(self) -> Future[Any]:
        ...

    @property
    @abstractmethod
    def position(self) -> Future[int]:
        ...

    @property
    @abstractmethod
    def is_moving(self) -> Future[bool]:
        ...

    def convert(self, p: Annotated[float, "mm"]) -> int:
        return int(p * 1000 * self.STEPS_PER_UM)


class FPGAControlled:
    com: COM

    @final
    def __init__(self, fpga_com: COM) -> None:
        self.com = fpga_com

    @property
    def _executor(self) -> NoReturn:
        raise AttributeError
