from __future__ import annotations

import asyncio
from dataclasses import dataclass
from logging import getLogger
from typing import Literal, NamedTuple

import numpy as np

from .base.instruments_types import SerialPorts
from .imaging.camera.dcam import Cameras, UInt16Array
from .imaging.fpga import FPGA
from .imaging.laser import Laser, Lasers
from .imaging.xstage import XStage
from .imaging.ystage import YStage

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


# Due to the optical arrangement, the actual channel ordering
# is not in order of increasing wavelength.
CHANNEL = {0: 1, 1: 3, 2: 2, 3: 0}


class Imager:
    UM_PER_PX = 0.375

    @classmethod
    async def ainit(cls, ports: dict[SerialPorts, str], init_cam: bool = True) -> Imager:
        to_init = (
            FPGA.ainit(ports["fpgacmd"], ports["fpgaresp"]),
            XStage.ainit(ports["x"]),
            YStage.ainit(ports["y"]),
            Laser.ainit("g", ports["laser_g"]),
            Laser.ainit("r", ports["laser_r"]),
        )

        if init_cam:
            fpga, x, y, laser_g, laser_r, cams = await asyncio.gather(*to_init, Cameras.ainit())
            return cls(fpga, x, y, Lasers(g=laser_g, r=laser_r), cams)

        fpga, x, y, laser_g, laser_r = await asyncio.gather(*to_init)
        return cls(fpga, x, y, Lasers(g=laser_g, r=laser_r), cams=None)

    def __init__(self, fpga: FPGA, x: XStage, y: YStage, lasers: Lasers, cams: Cameras | None) -> None:
        self.fpga = fpga
        self.tdi = self.fpga.tdi
        self.optics = self.fpga.optics
        self.lasers = lasers

        self.x = x
        self.y = y
        self.z_tilt = self.fpga.z_tilt
        self.z_obj = self.fpga.z_obj

        self.cams = cams
        self.lock = asyncio.Lock()

    async def initialize(self) -> None:
        async with self.lock:
            logger.info("Starting imager initialization.")
            await asyncio.gather(
                self.x.initialize(),
                self.y.initialize(),
                self.z_tilt.initialize(),
                self.z_obj.initialize(),
                self.optics.initialize(),
            )
            logger.info("Imager initialization completed.")

    # def get_state(self) -> State:
    #     out = {
    #         "laser_power": (self.lasers.g.power, self.lasers.r.power),
    #         "x_pos": self.x.pos,
    #         "y_pos": self.y.pos,
    #         "z_pos": self.z_tilt.pos,
    #         "z_obj_pos": self.z_obj.pos,
    #     }
    #     return State.from_futures(**out)

    async def wait_ready(self) -> None:
        """Returns when no commands are pending return which indicates that all motors are idle.
        This is because all move commands are expected to return some value upon completion.
        """
        logger.info("Waiting for all motions to complete.")
        await self.x.com.wait()
        await self.y.com.wait()
        await self.fpga.com.wait()
        logger.info("All motions completed.")

    async def take(
        self,
        n_bundles: int,
        dark: bool = False,
        channels: frozenset[Literal[0, 1, 2, 3]] = frozenset((0, 1, 2, 3)),
    ) -> UInt16Array:
        assert self.cams is not None
        if self.lock.locked():
            logger.info("Waiting for the previous imaging operation to complete.")

        async with self.lock:
            if not 0 < n_bundles < 1500:
                raise ValueError("n_bundles should be between 0 and 1500.")

            logger.info(f"Taking an image with {n_bundles} from channel(s) {channels}.")

            c = [CHANNEL[x] for x in sorted(channels)]
            if (0 in c or 1 in c) and (2 in c or 3 in c):
                cam = 2
            elif 0 in c or 1 in c:
                cam = 0
            elif 2 in c or 3 in c:
                cam = 1
            else:
                raise ValueError("Invalid channel(s).")

            # TODO: Compensate actual start position.
            n_bundles += 1  # To flush CCD.
            await self.wait_ready()

            pos = await self.y.pos
            n_px_y = n_bundles * self.cams.BUNDLE_HEIGHT
            # Need overshoot for TDI to function properly.
            end_y_pos = pos - self.calc_delta_pos(n_px_y) - 100000
            assert end_y_pos > -7e6

            await asyncio.gather(self.tdi.prepare_for_imaging(n_px_y, pos), self.y.set_mode("IMAGING"))
            cap = self.cams.acapture(n_bundles, fut_capture=self.y.move(end_y_pos, slowly=True), cam=cam)

            if dark:
                imgs = await cap
            else:
                async with self.optics.open_shutter():
                    imgs = await cap

            logger.info(f"Done taking an image.")
            await self.y.move(end_y_pos + 100000)  # Correct for overshoot.
            imgs = np.flip(imgs, axis=1)
            if cam == 1:
                return imgs[[x - 2 for x in c], :-128, :]  # type: ignore
            return imgs[:, :-128, :]  # Remove oversaturated first bundle.

    @staticmethod
    def calc_delta_pos(n_px_y: int) -> int:
        return int(n_px_y * Imager.UM_PER_PX * YStage.STEPS_PER_UM)

    @property
    async def pos(self) -> Position:
        names = ("x", "y", "z_tilt", "z_obj")
        res = await asyncio.gather(self.x.pos, self.y.pos, self.z_tilt.pos, self.z_obj.pos)
        return Position(**dict(zip(names, res)))  # type: ignore

    async def autofocus(self, channel: Literal[0, 1, 2, 3] = 1) -> tuple[int, UInt16Array]:
        """Moves to z_max and takes 232 (2048 × 5) images while moving to z_min.
        Returns the z position of maximum intensity and the images.
        """
        assert self.cams is not None
        if self.lock.locked():
            logger.info("Waiting for the previous imaging operation to complete.")

        async with self.lock:
            logger.info(f"Starting autofocus using data from {channel=}.")
            if channel not in (0, 1, 2, 3):
                raise ValueError(f"Invalid channel {channel}.")

            await self.wait_ready()

            n_bundles, height = 232, 5
            z_min, z_max = 2621, 60292
            cam = 0 if CHANNEL[channel] in (0, 1) else 1

            async with self.z_obj.af_arm(z_min=z_min, z_max=z_max) as start_move:
                async with self.optics.open_shutter():
                    img = await self.cams.acapture(
                        n_bundles, height, fut_capture=start_move, mode="FOCUS_SWEEP", cam=cam
                    )

            intensity = np.mean(
                np.reshape(img[CHANNEL[channel] - 2 * cam], (n_bundles, height, 2048)), axis=(1, 2)
            )
            target = int(z_max - (((z_max - z_min) / n_bundles) * np.argmax(intensity) + z_min))
            logger.info(f"Done autofocus. Optimum={target}")
            if not 10000 < target < 50000:
                logger.info(f"Target too close to edge, considering moving the tilt motors.")
            return (target, intensity)
