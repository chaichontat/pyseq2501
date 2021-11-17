from __future__ import annotations

import time
from enum import Enum, IntEnum, auto
from logging import Logger
from os import getcwd
from typing import Callable, Optional

from pyseq import HiSeq, get_com_ports
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

from stage import BetterYstage


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


class FriendlyHiSeq(HiSeq):
    def __init__(self, console: Console, name: str = "HiSeq2500", logger: Optional[Logger] = None) -> None:
        self.com_ports = get_com_ports("HiSeq2500")
        self.console = console
        self.logger = Logger = logger

        self.y = BetterYstage(self.com_ports["ystage"], logger=self.logger)
        self.f = FPGA(self.com_ports["fpgacommand"], self.com_ports["fpgaresponse"], logger=Logger)
        self.x = Xstage(self.com_ports["xstage"], logger=Logger)
        self.lasers = {
            "green": Laser(self.com_ports["laser1"], color="green", logger=Logger),
            "red": Laser(self.com_ports["laser2"], color="red", logger=Logger),
        }
        self.z = Zstage(self.f.serial_port, logger=Logger)
        self.obj = OBJstage(self.f.serial_port, logger=Logger)
        self.optics = Optics(self.f.serial_port, logger=Logger)
        self.cam1 = None
        self.cam2 = None
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
        self.check_COM()

    def gen_initialize_seq(self, skip: Optional[list[Components]] = None) -> dict[str, Callable[[], None]]:
        if skip is None:
            skip = list()

        def fpga() -> None:
            self.f.initialize()
            self.f.LED(1, "green")
            self.f.LED(2, "green")

        def xy_stage() -> None:
            self.y.command("OFF")
            homed = self.x.initialize()
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
            while not self.y.check_position():
                time.sleep(1)
            self.y.position = self.y.read_position()
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
                self.y.move(y)
                self.console.log("y complete")
            if x is not None:
                self.x.move(x)
                self.console.log("x complete")
            if z is not None:
                self.z.move([z, z, z])
                self.console.log("z complete")

    def take_picture(self, n_frames, image_name=None):
        y = self.y
        x = self.x
        obj = self.obj
        f = self.f
        op = self.optics
        cam1 = self.cam1
        cam2 = self.cam2

        if image_name is None:
            image_name = time.strftime("%Y%m%d_%H%M%S")

        msg = "HiSeq::TakePicture::"
        # Make sure TDI is synced with Ystage
        y_pos = self.y.read_position()
        if abs(y_pos - f.read_position()) > 10:
            self.message(msg + "Attempting to sync TDI and stage")
            f.write_position(y_pos)
        else:
            self.message(False, msg + "TDI and stage are synced")

        # TO DO, double check gains and velocity are set
        # Set gains and velocity of image scanning for ystage
        y.set_mode("imaging")
        # response = y.command('GAINS(5,10,5,2,0)')
        # response = y.command('V0.15400')

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
        end_y_pos = int(y_pos - n_triggers * self.resolution * y.spum - 300000)
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
        y.move(end_y_pos)

        ################################
        ### Stop Imaging ###############
        ################################
        # Close laser shutter
        f.command("SWLSRSHUT 0")
        time.sleep(1)

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

        # Reset gains & velocity for ystage
        y.set_mode("moving")
        # y.command('GAINS(5,10,7,1.5,0)')
        # y.command('V1')

        meta_f.close()

        return image_complete == 2
