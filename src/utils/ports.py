from __future__ import annotations

from dataclasses import asdict, dataclass
from enum import Enum, auto, unique


@unique
class Valve(Enum):
    A24 = auto()
    A10 = auto()
    B24 = auto()
    B10 = auto()


@dataclass(frozen=True)
class Ports:
    x: str
    y: str
    pumps: tuple[str, str]
    valves: dict[Valve, str]
    fpga: tuple[str, str]
    lasers: tuple[str, str]
    arm9chem: str

    def __post_init__(self):
        for name, obj in asdict(self).items():
            if isinstance(obj, dict):
                [self.check(x, name) for x in obj.values()]
            elif isinstance(obj, tuple):
                [self.check(x, name) for x in obj]
            else:
                self.check(obj, name)

    @staticmethod
    def check(x: str, name: str):
        if not x.startswith("COM"):
            raise ValueError(f"What kind of sorcery is this port {x} for {name}")


ports = {
    "xstage": "COM9",
    "ystage": "COM10",
    "pumpa": "COM19",
    "pumpb": "COM22",
    "valvea24": "COM20",
    "valvea10": "COM18",
    "valveb24": "COM23",
    "valveb10": "COM21",
    "fpgacommand": "COM11",
    "fpgaresponse": "COM13",
    "laser1": "COM14",
    "laser2": "COM17",
    "arm9chem": "COM8",
}
