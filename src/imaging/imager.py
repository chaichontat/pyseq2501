from concurrent.futures import Future
from dataclasses import asdict, dataclass
from typing import get_args

from src.imaging.camera.dcam import Camera, Cameras
from src.imaging.fpga.fpga import FPGA
from src.imaging.ystage import YStage
from src.instruments import Instruments
from src.utils.ports import Ports

from .fpga.optics import Optics
from .laser import Laser, Lasers


@dataclass
class Channel:
    laser: Laser
    optics: Optics


# ports = {
#     "xstage": "COM9",
#     "ystage": "COM10",
#     "pumpa": "COM19",
#     "pumpb": "COM22",
#     "valvea24": "COM20",
#     "valvea10": "COM18",
#     "valveb24": "COM23",
#     "valveb10": "COM21",
#     "fpgacommand": "COM11",
#     "fpgaresponse": "COM13",
#     "laser1": "COM14",
#     "laser2": "COM17",
#     "arm9chem": "COM8",
# }


ports = Ports(
    x="COM9",
    y="COM10",
    fpga=("COM11", "COM13"),
    laser_g="COM14",
    laser_r="COM17",
)


class Imager:
    fpga: FPGA

    def __init__(self, ports: Ports) -> None:
        assert set(asdict(ports).keys()) == set(get_args(Instruments))
        self.fpga = FPGA(*ports.fpga)

        self.x = YStage(ports.x)
        self.y = YStage(ports.y)
        self.z = self.fpga.z

        self.cams = Cameras(Camera(0), Camera(1))
        self.lasers = Lasers(Laser(ports.laser_g), Laser(ports.laser_r))

    def initialize(self) -> Future[None]:
        [x.initialize for x in (self.x, self.y, self.z, self.cams, self.lasers, self.fpga)]
