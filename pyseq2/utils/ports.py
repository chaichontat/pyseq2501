#%%
import asyncio
import time
from pprint import pprint
from typing import TypeVar, cast

import serial.tools.list_ports

from pyseq2.base.instruments_types import SerialPorts

T = TypeVar("T")


serial_names: dict[SerialPorts, str] = dict(
    x="IL000001A",
    y="IL000002A",
    laser_g="IL000006A",
    laser_r="IL000007A",
    arm9chem="ARM9CHEMA",
    arm9pe="PCIOA",
    pumpa="KLOEHNAA",
    pumpb="KLOEHNBA",
    valve_a1="VICIA1A",
    valve_a2="VICIA2A",
    valve_b1="VICIB1A",
    valve_b2="VICIB2A",
    fpgacmd="IL000004A",
    fpgaresp="IL000005A",
)  # type: ignore # Dict is invariant.


async def get_ports(timeout: int | float = 1, show_all=False) -> dict[SerialPorts, str]:
    """
    See https://pyserial.readthedocs.io/en/latest/tools.html for more details.

    Returns:
        Ports: Dataclass of relevant components and their COM ports.
    """
    t0 = time.monotonic()
    while time.monotonic() - t0 < timeout:
        ports = {
            dev.serial_number: dev.name
            for dev in await asyncio.get_running_loop().run_in_executor(
                None, serial.tools.list_ports.comports
            )
            if dev.serial_number is not None
        }
        try:
            res = cast(dict[str, str], {name: ports[id_] for name, id_ in serial_names.items()})
            if show_all:
                pprint(f"{ports}")
            return cast(dict[SerialPorts, str], res)
        except KeyError as e:
            print(f"Cannot find {e}.")
            time.sleep(0.5)

    raise Exception(f"Cannot find ports after {timeout} seconds.")


if __name__ == "__main__":
    print(asyncio.run(get_ports(show_all=True)))

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
