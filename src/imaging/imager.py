import time
from dataclasses import dataclass

from src.imaging.camera.dcam import Cameras
from src.imaging.fpga import FPGA
from src.imaging.xstage import XStage
from src.imaging.ystage import YStage
from src.utils.ports import Ports

from .fpga.optics import Optics
from .laser import Laser, Lasers


@dataclass
class Channel:
    laser: Laser
    optics: Optics


class Imager:
    fpga: FPGA
    UM_PER_PX = 0.375

    def __init__(self, ports: Ports) -> None:
        # assert set(asdict(ports).keys()) == set(get_args(Instruments))
        self.fpga = FPGA(*ports.fpga)
        self.tdi = self.fpga.tdi
        self.optics = self.fpga.optics

        self.x = XStage(ports.x)
        self.y = YStage(ports.y)
        self.z = self.fpga.z

        self.cams = Cameras()
        self.lasers = Lasers(Laser(ports.laser_g), Laser(ports.laser_r))

    # def initialize(self) -> Future[None]:
    #     [x.initialize for x in (self.x, self.y, self.z, self.cams, self.lasers, self.fpga)]

    def take_image(self, n_bundles: int):
        pos = self.y.position
        self.y._mode = "IMAGING"

        pos = pos.result()
        n_px_y = n_bundles * self.cams.BUNDLE_HEIGHT
        end_y_pos = pos - (delta := self.calc_delta_pos(n_px_y))
        fpga_ready = self.tdi.prepare_for_imaging(n_px_y, pos)

        with self.cams.alloc(n_bundles):
            fpga_ready.result()
            with self.optics.open_shutter(), self.cams.capture():
                self.y.move(end_y_pos, slowly=True).result()
                # TODO: Check when exactly does y start moving. Right after receiving signal or after reply.
                time.sleep(delta / 200200)

    @staticmethod
    def calc_delta_pos(n_px_y: int) -> int:
        return int(n_px_y * Imager.UM_PER_PX * YStage.STEPS_PER_UM - 300000)
