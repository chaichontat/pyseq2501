from __future__ import annotations

import time
from concurrent.futures import ThreadPoolExecutor
from dataclasses import dataclass
from logging import getLogger
from typing import NamedTuple

import numpy as np

from .com.thread_mgt import run_in_executor
from .imaging.camera.dcam import Cameras, Mode, UInt16Array
from .imaging.fpga import FPGA
from .imaging.laser import Laser, Lasers
from .imaging.xstage import XStage
from .imaging.ystage import YStage
from .utils.ports import Ports
from .utils.utils import not_none

logger = getLogger("Imager")


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

    @property
    def all_still(self) -> bool:
        x, y, z = self.x.is_moving, self.y.is_moving, self.z_tilt.is_moving
        return not any((x.result(60), y.result(60), z.result(60)))

    # TODO add more ready checks.
    def take(self, n_bundles: int, dark: bool = False) -> UInt16Array:
        logger.info(f"Taking image with {n_bundles} bundles.")
        n_bundles += 1  # To flush CCD.
        while not self.all_still:
            logger.info("Started taking an image while stage is moving. Waiting.")
            time.sleep(0.5)

        self.y.set_mode("IMAGING")
        pos = self.y.pos
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

    @property
    @run_in_executor
    def pos(self) -> Position:
        res = dict(x=self.x.pos, y=self.y.pos, z_tilt=self.z_tilt.pos, z_obj=self.z_obj.pos)
        res = {k: v.result() for k, v in res.items()}
        return Position(**res)  # type: ignore

    def autofocus(self) -> tuple[int, UInt16Array]:
        """Moves to z_max and takes 232 (2048 × 5) images while moving to z_min.

        Returns the z position of maximum intensity and the images.

        """
        n_bundles, height = 232, 5
        z_min, z_max = 2621, 60292
        self.cams[0].properties.update({"sensor_mode": 6, "exposure_time": 0.002, "partial_area_vsize": 5})
        self.fpga.com.send("ZTRG 0")
        self.fpga.com.send("ZYT 0 3")
        self.fpga.com.send(f"ZMV {z_max}")
        self.fpga.com.send("SWYZ_POS 1")

        with self.cams._alloc(n_bundles, height=height) as bufs:
            with self.optics.open_shutter():
                self.fpga.com.send("ZSTEP 541158")
                self.fpga.com.send(f"ZTRG {z_max}")
                self.fpga.com.send("ZYT 0 3")
                with self.cams[0].capture():
                    self.fpga.com.send(f"ZMV {z_min}")
                    while (self.cams[0].n_frames_taken) < n_bundles:
                        time.sleep(0.01)

        intensity = np.mean(np.reshape(bufs[0], (n_bundles, height, 4096)), axis=(1, 2))
        target = np.argmax(intensity)[0]

        self.fpga.com.send("ZSTEP 6442353")
        return (z_max - (((z_max - z_min) / n_bundles) * target + z_min), intensity)
