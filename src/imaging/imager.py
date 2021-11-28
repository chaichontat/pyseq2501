import time
from concurrent.futures import Future
from dataclasses import dataclass

from src.imaging.camera.dcam import Cameras, FourImages, Mode
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

        self.lasers = Lasers(Laser(ports.laser_g), Laser(ports.laser_r))
        self.cams = Cameras()

    def initialize(self) -> None:
        self.x.initialize()
        self.y.initialize()
        self.lasers.initialize()

    def take_image(self, n_bundles: int) -> FourImages:
        pos = self.y.position
        self.y._mode = "IMAGING"
        self.cams.mode = Mode.TDI
        pos = pos.result()
        n_px_y = n_bundles * self.cams.BUNDLE_HEIGHT
        end_y_pos = pos - (delta := self.calc_delta_pos(n_px_y)) - 300000

        fpga_ready = self.tdi.prepare_for_imaging(n_px_y, pos).result()
        with self.optics.open_shutter():
            return self.cams.capture(
                n_bundles,
                start_capture=lambda: self.y.move(end_y_pos, slowly=True),
            ).result()
            # while not fut.done():
            #     self.y.com.repl(self.y.cmd.READ_POS)

    @staticmethod
    def calc_delta_pos(n_px_y: int) -> int:
        return int(n_px_y * Imager.UM_PER_PX * YStage.STEPS_PER_UM)
