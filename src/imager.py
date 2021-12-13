from __future__ import annotations

import time
from dataclasses import dataclass
from logging import getLogger

from src.utils.utils import not_none

from .imaging.camera.dcam import Cameras, Mode, UInt16Array
from .imaging.fpga import FPGA
from .imaging.fpga.optics import Optics
from .imaging.laser import Laser, Lasers
from .imaging.xstage import XStage
from .imaging.ystage import YStage
from .utils.ports import Ports
from .utils.utils import not_none

logger = getLogger("Imager")


@dataclass
class Channel:
    laser: Laser
    optics: Optics


@dataclass(frozen=True)
class State:
    laser_power: tuple[int, int]
    x_pos: int
    y_pos: int
    z_pos: tuple[int, int, int]
    z_obj_pos: int

    @classmethod
    def from_futures(cls, *args, **kwargs) -> State:
        args = map(lambda x: x.result(), args)
        kwargs = {k: v.result() for k, v in kwargs.items()}
        return cls(*args, **kwargs)


class Imager:
    UM_PER_PX = 0.375

    def __init__(self, ports: Ports, init_cam: bool = True) -> None:
        self.fpga = FPGA(*ports.fpga)
        self.fpga.initialize()
        self.tdi = self.fpga.tdi
        self.optics = self.fpga.optics

        self.x = XStage(ports.x)
        self.y = YStage(ports.y)
        self.z = self.fpga.z
        self.z_obj = self.fpga.z_obj

        self.lasers = Lasers(Laser("laser_g", ports.laser_g), Laser("laser_r", ports.laser_r))
        if init_cam:
            self.cams = Cameras()

    def initialize(self) -> None:
        self.x.initialize()
        self.y.initialize()
        self.lasers.initialize()

    def get_state(self) -> State:
        out = {
            "laser_power": (self.lasers.g.power, self.lasers.r.power),
            "x_pos": self.x.position,
            "y_pos": self.y.position,
            "z_pos": self.z.position,
            "z_obj_pos": self.z_obj.position,
        }
        return State.from_futures(**out)

    @property
    def all_still(self) -> bool:
        x, y, z = self.x.is_moving, self.y.is_moving, self.z.is_moving
        return not any((x.result(60), y.result(60), z.result(60)))

    # TODO add more ready checks.
    def take(self, n_bundles: int, dark: bool = False) -> UInt16Array:
        logger.info(f"Taking image with {n_bundles} bundles.")
        n_bundles += 1  # To flush CCD.
        while not self.all_still:
            logger.info("Started taking an image while stage is moving. Waiting.")
            time.sleep(0.5)

        self.y.set_mode("IMAGING")
        pos = self.y.position
        pos = pos.result(60)
        assert pos is not None
        n_px_y = n_bundles * self.cams.BUNDLE_HEIGHT
        end_y_pos = pos - (delta := self.calc_delta_pos(n_px_y)) - 100000
        fut = self.tdi.prepare_for_imaging(n_px_y, pos)
        self.cams.mode = Mode.TDI
        fut.result(60)

        cap = lambda: self.cams.capture(
            n_bundles, start_capture=lambda: self.y.move(end_y_pos, slowly=True)
        ).result(int(n_bundles / 2))

        if dark:
            imgs = cap()
        else:
            with self.optics.open_shutter():
                imgs = cap()

        if not_none(res := self.fpga.tdi.n_pulses.result(1)) != (exp := 128 * n_bundles):
            logger.warning(f"Number of trigger pulses mismatch. Expected: {exp} Got {res}.")

        logger.info(f"Done taking an image.")
        return imgs[:, :-128, :]  # Remove first oversaturated bundle.

    @staticmethod
    def calc_delta_pos(n_px_y: int) -> int:
        return int(n_px_y * Imager.UM_PER_PX * YStage.STEPS_PER_UM)
