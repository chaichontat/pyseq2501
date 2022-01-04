from __future__ import annotations

from concurrent.futures import ThreadPoolExecutor
from dataclasses import dataclass
from logging import getLogger
from typing import Literal, NamedTuple

import numpy as np

from .com.thread_mgt import run_in_executor
from .imaging.camera.dcam import Cameras, UInt16Array
from .imaging.fpga import FPGA
from .imaging.laser import Laser, Lasers
from .imaging.xstage import XStage
from .imaging.ystage import YStage
from .utils.ports import Ports
from .utils.utils import not_none

logger = getLogger(__name__)


class Position(NamedTuple):
    x: int
    y: int
    z_tilt: tuple[int, int, int]
    z_obj: int


@dataclass(frozen=True)
class State:
    laser_power: tuple[int, int]
    pos: Position

    @classmethod
    def from_futures(cls, *args, **kwargs) -> State:
        args = map(lambda x: x.result(), args)
        kwargs = {k: v.result() for k, v in kwargs.items()}
        return cls(*args, **kwargs)


class Imager:
    UM_PER_PX = 0.375

    def __init__(self, ports: Ports, init_cam: bool = True) -> None:
        self.fpga = FPGA(*ports.fpga)
        self.tdi = self.fpga.tdi
        self.optics = self.fpga.optics

        self.x = XStage(ports.x)
        self.y = YStage(ports.y)
        self.z_tilt = self.fpga.z_tilt
        self.z_obj = self.fpga.z_obj

        self.lasers = Lasers(Laser("laser_g", ports.laser_g), Laser("laser_r", ports.laser_r))
        if init_cam:
            self.cams = Cameras()

        self._executor = ThreadPoolExecutor(max_workers=1)

    def initialize(self) -> None:
        self.x.initialize()
        self.y.initialize()
        self.z_tilt.initialize()
        self.z_obj.initialize()
        self.optics.initialize()

    def get_state(self) -> State:
        out = {
            "laser_power": (self.lasers.g.power, self.lasers.r.power),
            "x_pos": self.x.pos,
            "y_pos": self.y.pos,
            "z_pos": self.z_tilt.pos,
            "z_obj_pos": self.z_obj.pos,
        }
        return State.from_futures(**out)

    def wait_all_idle(self) -> None:
        logger.info("Waiting for all motions to complete.")
        self.x.com._executor.submit(lambda: None).result(60)
        self.y.com._executor.submit(lambda: None).result(60)
        self.fpga.com._executor.submit(lambda: None).result(60)
        logger.info("All motions completed.")

    def take(self, n_bundles: int, dark: bool = False, cam: Literal[0, 1, 2] = 2) -> UInt16Array:
        logger.info(f"Taking an image with {n_bundles} bundles.")
        n_bundles += 1  # To flush CCD.
        self.wait_all_idle()

        self.y.set_mode("IMAGING")
        pos = self.y.pos.result(60)
        assert pos is not None
        n_px_y = n_bundles * self.cams.BUNDLE_HEIGHT
        end_y_pos = pos - (delta := self.calc_delta_pos(n_px_y)) - 100000
        fut = self.tdi.prepare_for_imaging(n_px_y, pos)
        fut.result(60)

        cap = lambda: self.cams.capture(
            n_bundles, start_capture=lambda: self.y.move(end_y_pos, slowly=True), cam=cam
        ).result(int(n_bundles / 2))

        if dark:
            imgs = cap()
        else:
            with self.optics.open_shutter():
                imgs = cap()

        logger.info(f"Done taking an image.")
        imgs = np.flip(imgs, axis=1)
        return imgs[:, :-128, :]  # Remove oversaturated first bundle.

    @staticmethod
    def calc_delta_pos(n_px_y: int) -> int:
        return int(n_px_y * Imager.UM_PER_PX * YStage.STEPS_PER_UM)

    @property
    @run_in_executor
    def pos(self) -> Position:
        res = dict(x=self.x.pos, y=self.y.pos, z_tilt=self.z_tilt.pos, z_obj=self.z_obj.pos)
        res = {k: v.result() for k, v in res.items()}
        return Position(**res)  # type: ignore

    def autofocus(self, channel: Literal[0, 1, 2, 3] = 1) -> tuple[int, UInt16Array]:
        """Moves to z_max and takes 232 (2048 × 5) images while moving to z_min.
        Returns the z position of maximum intensity and the images.
        """
        logger.info(f"Starting autofocus using data from {channel=}.")
        self.wait_all_idle()

        n_bundles, height = 232, 5
        z_min, z_max = 2621, 60292
        cam = 0 if channel in (0, 1) else 1

        with self.z_obj.af_arm(z_min=z_min, z_max=z_max) as start_move:
            with self.optics.open_shutter():
                img = self.cams.capture(
                    n_bundles, height, start_capture=start_move, mode="FOCUS_SWEEP", cam=cam
                ).result(int(n_bundles / 2))

        intensity = np.mean(np.reshape(img[channel - 2 * cam], (n_bundles, height, 2048)), axis=(1, 2))
        target = int(z_max - (((z_max - z_min) / n_bundles) * np.argmax(intensity) + z_min))
        logger.info(f"Done autofocus. Optimum={target}")
        return (target, intensity)
