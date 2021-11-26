#%%
import inspect
import time
from dataclasses import dataclass
from typing import Type, TypeVar, cast

import serial.tools.list_ports

T = TypeVar("T")


@dataclass
class Ports:
    x: str
    y: str
    fpga: tuple[str, str]
    laser_g: str
    laser_r: str

    @classmethod
    def from_raw(cls: Type[T], res: dict[str, str]) -> T:
        fpga = (res["fpgacommand"], res["fpgaresponse"])
        kwargs = {k: v for k, v in res.items() if k in inspect.signature(cls).parameters}
        return cls(fpga=fpga, **kwargs)


name_map = dict(
    x="IL000001A",
    y="IL000002A",
    pumpa="KLOEHNAA",
    pumpb="KLOEHNBA",
    valvea24="VICIA2A",
    valvea10="VICIA1A",
    valveb24="VICIB2A",
    valveb10="VICIB1A",
    fpgacommand="IL000004A",
    fpgaresponse="IL000005A",
    laser_g="IL000006A",
    laser_r="IL000007A",
    arm9chem="ARM9CHEMA",
)


def get_ports(timeout: int | float = 0) -> Ports:
    """
    See https://pyserial.readthedocs.io/en/latest/tools.html for more details.

    Returns:
        Ports: Dataclass of relevant components and their COM ports.
    """
    t0 = time.time()
    while time.time() - t0 < timeout:
        ports = {
            dev.serial_number: dev.name
            for dev in serial.tools.list_ports.comports()
            if dev.serial_number is not None
        }
        try:
            res = cast(dict[str, str], {name: ports[id_] for name, id_ in name_map.items()})
            return Ports.from_raw(res)
        except KeyError as e:
            print(e)
            time.sleep(0.5)

    raise Exception(f"Cannot find ports after {timeout} seconds.")


if "__name__" == "__main__":
    print(get_ports())

# REGEX_COM = re.compile(r"\((COM\d{1,2})\)")
# REGEX_ID = re.compile(r"\+(\w+)\\")


# def find_ports() -> Ports:
#     import wmi

#     devices = wmi.WMI().CIM_LogicalDevice()
#     com_ports = {
#         REGEX_ID.search(d.deviceid).group(1): REGEX_COM.search(d.caption).group(1)  # type: ignore[union-attr]
#         for d in devices
#         if d.caption is not None and "USB Serial Port" in d.caption
#     }

#     res = {name: com_ports[id_] for name, id_ in name_map.items()}
#     return Ports.from_raw(res)


# # @unique
# # class Valve(Enum):
# #     A24 = auto()
# #     A10 = auto()
# #     B24 = auto()
# #     B10 = auto()


# # @dataclass(frozen=True)
# # class Ports:
# #     x: str
# #     y: str
# #     pumps: tuple[str, str]
# #     valves: dict[Valve, str]
# #     fpga: tuple[str, str]
# #     lasers: tuple[str, str]
# #     arm9chem: str

# #     def __post_init__(self):
# #         for name, obj in asdict(self).items():
# #             if isinstance(obj, dict):
# #                 [self.check(x, name) for x in obj.values()]
# #             elif isinstance(obj, tuple):
# #                 [self.check(x, name) for x in obj]
# #             else:
# #                 self.check(obj, name)

# #     @staticmethod
# #     def check(x: str, name: str):
# #         if not x.startswith("COM"):
# #             raise ValueError(f"What kind of sorcery is this port {x} for {name}")


# # ports = {
# #     "xstage": "COM9",
# #     "ystage": "COM10",
# #     "pumpa": "COM19",
# #     "pumpb": "COM22",
# #     "valvea24": "COM20",
# #     "valvea10": "COM18",
# #     "valveb24": "COM23",
# #     "valveb10": "COM21",
# #     "fpgacommand": "COM11",
# #     "fpgaresponse": "COM13",
# #     "laser1": "COM14",
# #     "laser2": "COM17",
# #     "arm9chem": "COM8",
# # }
# #%%

# %%
