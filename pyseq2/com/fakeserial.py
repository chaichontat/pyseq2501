import time
from dataclasses import dataclass, field
from logging import Logger
from typing import Optional

from pyseq2.base.instruments_types import SerialInstruments


def assert_(x: bool):
    assert x


# def y_resp(s: str) -> str:
#     match s:
#         case "G":
#             return "1G"
#         case x if lambda x: x.startswith("D"):
#             return int(x[1:])
#         case _:
#             return ""


@dataclass
class FakeSerial:
    name: SerialInstruments
    port_tx: str
    port_rx: Optional[str] = None
    timeout: Optional[int | float] = 1
    _buffer: str = field(default="", init=False)

    def __post_init__(self) -> None:
        print("Using fake serial!")
        assert self.port_tx.startswith("COM")

    def write(self, s: str) -> None:
        time.sleep(0.5)
        # TODO Put in transformations.
        self._buffer += s

    def flush(self) -> None:
        self._buffer = ""

    def readline(self, fail: bool = False) -> str:
        time.sleep(0.5)
        x = self._buffer
        self.flush()
        return x

    def readlines(self, fail: bool = False) -> str:
        time.sleep(0.5)
        x = self._buffer
        self.flush()
        return x
