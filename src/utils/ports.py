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
#%%

import configparser

machine = "HiSeq2500"
cfg = """[HiSeq2500]
xstage = IL000001A
ystage = IL000002A
pumpa = KLOEHNAA
pumpb = KLOEHNBA
valvea24 = VICIA2A
valvea10 = VICIA1A
valveb24 = VICIB2A
valveb10 = VICIB1A
fpgacommand = IL000004A
fpgaresponse = IL000005A
laser1 = IL000006A
laser2 = IL000007A
arm9chem = ARM9CHEMA
"""
com_names = configparser.ConfigParser()
com_names.read_string(cfg)

# Get list of connected devices
import wmi

conn = wmi.WMI()
devices = conn.CIM_LogicalDevice()
# Get lists of valid COM ports
ids = []
com_ports = []
for d in devices:
    try:
        if "USB Serial Port" in d.caption:
            ids.append(d.deviceid)
            caption = d.caption
            id_start = caption.find("(") + 1
            id_end = caption.find(")")
            caption = caption[id_start:id_end]
            com_ports.append(caption)
    except:
        pass

# Match instruments to ports
matched_ports = {}
for instrument, com_name in com_names.items(machine):
    try:
        ind = [i for i, id in enumerate(ids) if com_name in id]
        if len(ind) == 1:
            ind = ind[0]
        else:
            print("Multiple COM Port matches for", instrument)
            raise ValueError
        matched_ports[instrument] = com_ports[ind]
    except ValueError:
        matched_ports[instrument] = None
        print("Could not find port for", instrument)
print(matched_ports)
# %%
