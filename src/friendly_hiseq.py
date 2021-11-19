from __future__ import annotations

import logging
import time
from contextlib import contextmanager
from enum import Enum, IntEnum, auto
from os import getcwd
from typing import Callable, Generator, Iterable, Iterator, Optional

from pyseq import HiSeq, get_com_ports
from pyseq.dcam import HamamatsuCamera
from pyseq.fpga import FPGA
from pyseq.laser import Laser
from pyseq.objstage import OBJstage
from pyseq.optics import Optics
from pyseq.pump import Pump
from pyseq.temperature import Temperature
from pyseq.valve import Valve
from pyseq.xstage import Xstage
from pyseq.ystage import Ystage
from pyseq.zstage import Zstage
from rich.console import Console

from instruments.stage import BetterYstage


class Components(IntEnum):
    CAMERAS = auto()
    FPGA = auto()
    XY_STAGE = auto()
    LASERS = auto()
    PUMPS = auto()
    VALVES = auto()
    Z_STAGE = auto()
    OBJECTIVE = auto()
    OPTICS = auto()
    TEMP_CTRL = auto()
    SYNC_TDI = auto()


Logger = logging.getLogger(__name__)


class FriendlyHiSeq(HiSeq):
    def __init__(self, console: Console, name: str = "HiSeq2500") -> None:
        self.com_ports = get_com_ports("HiSeq2500")
        self.console = console

        self.y = BetterYstage(self.com_ports["ystage"])
        self.f = FPGA(self.com_ports["fpgacommand"], self.com_ports["fpgaresponse"], logger=Logger)
        self.x = Xstage(self.com_ports["xstage"], logger=Logger)
        self.lasers = {
            "green": Laser(self.com_ports["laser1"], color="green", logger=Logger),
            "red": Laser(self.com_ports["laser2"], color="red", logger=Logger),
        }
        self.z = Zstage(self.f, logger=Logger)
        self.obj = OBJstage(self.f, logger=Logger)
        self.optics = Optics(self.f, logger=Logger)
        # self.cams = [HamamatsuCamera(i, logger=Logger) for i in range(2)]
        self.cam1 = HamamatsuCamera(0, logger=Logger)
        self.cam2 = HamamatsuCamera(1, logger=Logger)
        self.cam1.left_emission = 687
        self.cam1.right_emission = 558
        self.cam2.left_emission = 610
        self.cam2.right_emission = 740
        self.cams = {0: self.cam1, 1: self.cam2}
        self.p = {
            "A": Pump(self.com_ports["pumpa"], "pumpA", logger=Logger),
            "B": Pump(self.com_ports["pumpb"], "pumpB", logger=Logger),
        }
        self.v10 = {
            "A": Valve(self.com_ports["valvea10"], "valveA10", logger=Logger),
            "B": Valve(self.com_ports["valveb10"], "valveB10", logger=Logger),
        }
        self.v24 = {
            "A": Valve(self.com_ports["valvea24"], "valveA24", logger=Logger),
            "B": Valve(self.com_ports["valveb24"], "valveB24", logger=Logger),
        }
        self.T = Temperature(self.com_ports["arm9chem"], logger=Logger)
        self.image_path = getcwd()  # path to save images in
        self.log_path = getcwd()  # path to save logs in
        self.fc_origin = {"A": [17571, -180000], "B": [43310, -180000]}
        self.tile_width = 0.769  # mm
        self.resolution = 0.375  # um/px
        self.bundle_height = 128
        self.nyquist_obj = 235  # 0.9 um (235 obj steps) is nyquist sampling distance in z plane
        self.logger = Logger
        self.channels = None
        self.AF = "partial"  # autofocus routine
        self.focus_tol = 0  # um, focus tolerance
        self.overlap = 0
        self.overlap_dir = "left"
        self.virtual = False  # virtual flag
        self.scan_flag = False  # imaging/scanning flag
        self.current_view = None  # latest images
        self.name = name
        # self.check_COM()

    def gen_initialize_seq(self, skip: Optional[list[Components]] = None) -> dict[str, Callable[[], None]]:
        if skip is None:
            skip = list()

        def fpga() -> None:
            self.f.initialize()
            self.f.LED(1, "green")
            self.f.LED(2, "green")

        def xy_stage() -> None:
            self.y.send("OFF")
            self.x.initialize()
            self.y.initialize()

        def lasers() -> None:
            self.lasers["green"].initialize()
            self.lasers["red"].initialize()

        def pumps() -> None:
            self.p["A"].initialize()
            self.p["B"].initialize()

        def valves() -> None:
            self.v10["A"].initialize()
            self.v10["B"].initialize()
            self.v24["A"].initialize()
            self.v24["B"].initialize()

        def sync_tdi() -> None:
            while not self.y.is_in_position:
                time.sleep(1)
            self.f.write_position(0)

        seq = {
            Components.CAMERAS: lambda: self.initializeCams(Logger=self.logger),
            Components.FPGA: fpga,
            Components.XY_STAGE: xy_stage,
            Components.LASERS: lasers,
            Components.PUMPS: pumps,
            Components.VALVES: valves,
            Components.Z_STAGE: lambda: self.z.initialize(),
            Components.OBJECTIVE: lambda: self.obj.initialize(),
            Components.OPTICS: lambda: self.optics.initialize(),
            Components.TEMP_CTRL: lambda: self.T.initialize(),
            Components.SYNC_TDI: sync_tdi,
        }

        return {
            f"Initializing {Components(comp).name}": func for comp, func in seq.items() if comp not in skip
        }

    def move(self, *, x: Optional[int] = None, y: Optional[int] = None, z: Optional[int] = None) -> None:
        """
        x is between 1000 and 5e4.
        y is between -7e6 and 7e6.
        z is between
        """
        with self.console.status("[bold green]Moving...") as status:
            if y is not None:
                self.y.position = y
                self.console.log("y complete")
            if x is not None:
                self.x.move(x)
                self.console.log("x complete")
            if z is not None:
                self.z.move([z, z, z])
                self.console.log("z complete")

    def take_picture(self, n_frames, image_name) -> bool:
        y = self.y
        f = self.f
        cam1 = self.cam1
        cam2 = self.cam2

        msg = "HiSeq::TakePicture::"
        # Make sure TDI is synced with Ystage
        y_pos = self.y.position
        if abs(y_pos - f.read_position()) > 10:
            self.message(msg + "Attempting to sync TDI and stage")
            f.write_position(y_pos)
        else:
            self.message(False, msg + "TDI and stage are synced")

        # TO DO, double check gains and velocity are set
        y._mode = "IMAGING"

        # Make sure cameras are ready (status = 3)
        while cam1.get_status() != 3:
            cam1.stopAcquisition()
            cam1.freeFrames()
            cam1.captureSetup()
        while cam2.get_status() != 3:
            cam2.stopAcquisition()
            cam2.freeFrames()
            cam2.captureSetup()

        if cam1.sensor_mode != "TDI":
            cam1.setTDI()
        if cam2.sensor_mode != "TDI":
            cam2.setTDI()

        # Set bundle height
        cam1.setPropertyValue("sensor_mode_line_bundle_height", self.bundle_height)
        cam2.setPropertyValue("sensor_mode_line_bundle_height", self.bundle_height)
        cam1.captureSetup()
        cam2.captureSetup()
        # Allocate memory for image data
        cam1.allocFrame(n_frames)
        cam2.allocFrame(n_frames)

        #
        # Arm stage triggers
        #
        # TODO check trigger y values are reasonable
        n_triggers = n_frames * self.bundle_height
        end_y_pos = int(y_pos - n_triggers * self.resolution * y.STEPS_PER_UM - 300000)
        f.TDIYPOS(y_pos)
        f.TDIYARM3(n_triggers, y_pos)

        meta_f = self.write_metadata(n_frames, image_name)

        ################################
        ### Start Imaging ##############
        ################################

        # Start cameras
        cam1.startAcquisition()
        cam2.startAcquisition()
        # Open laser shutter
        f.command("SWLSRSHUT 1")
        # move ystage (blocking)
        y.position = end_y_pos

        ################################
        ### Stop Imaging ###############
        ################################
        # Close laser shutter
        f.command("SWLSRSHUT 0")
        time.sleep(0.01)

        # Stop Cameras
        cam1.stopAcquisition()
        cam2.stopAcquisition()

        # Check if all frames were taken from camera 1 then save images
        if cam1.getFrameCount() != n_frames:
            self.message(False, msg, "Cam1 frames = ", cam1.getFrameCount())
            self.message(True, msg, "Cam1 image not taken")
            image_complete = False
        else:
            cam1.saveImage(image_name, self.image_path)
            image_complete = True
        # Check if all frames were taken from camera 2 then save images
        if cam2.getFrameCount() != n_frames:
            self.message(False, msg, "Cam2 frames = ", cam2.getFrameCount())
            self.message(True, msg, "Cam2 image not taken")
            image_complete += False
        else:
            cam2.saveImage(image_name, self.image_path)
            image_complete += True
        # Print out info pulses = triggers, not sure with CLINES is
        if image_complete:
            response = self.cam1.getFrameCount()
            meta_f.write("frame count 1 " + str(response) + "\n")
            response = self.cam2.getFrameCount()
            meta_f.write("frame count 2 " + str(response) + "\n")
            response = f.command("TDICLINES")
            meta_f.write("clines " + str(response) + "\n")
            response = f.command("TDIPULSES")
            meta_f.write("pulses " + str(response) + "\n")

        # Free up frames/memory
        cam1.freeFrames()
        cam2.freeFrames()

        y._mode = "MOVING"

        meta_f.close()

        return image_complete == 2

    @contextmanager
    def _capture_context(self, y_pos: int, n_frames: int) -> Iterator[None]:
        self.f.write_position(y_pos)  # TODO: Verify
        self.f.TDIYPOS(y_pos)
        self.f.TDIYARM3(n_frames * 128, y_pos)

        for c in self.cams.values():
            if c.get_status() != 3:
                raise Exception("Invalid camera state. What have you done!?")
            c.captureSetup()
            c.allocFrame(n_frames)

        yield

        for c in self.cams.values():
            c.freeFrames()

    @contextmanager
    def _acquire(self) -> Iterator[None]:
        [c.startAcquisition() for c in self.cams.values()]
        self.f.command("SWLSRSHUT 1")
        yield
        self.f.command("SWLSRSHUT 0")
        time.sleep(0.01)
        [c.stopAcquisition() for c in self.cams.values()]

    def better_take_image(self, n_frames: int, image_name: str) -> None:
        y_pos = self.y.position
        with self._capture_context(y_pos, n_frames):
            with self._acquire():
                self.y.move_slowly(
                    int(y_pos - n_frames * 128 * self.resolution * self.y.STEPS_PER_UM - 300000)
                )

            for c in self.cams.values():
                if c.getFrameCount() == n_frames:
                    c.saveImage(image_name, self.image_path)  # TODO: Don't write image right away.
                else:
                    raise Exception("Image not captured.")
