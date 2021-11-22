from contextlib import contextmanager
from ctypes import byref, c_int32, c_ulong, c_void_p
from enum import IntEnum
from typing import Literal

import numpy as np
from src.imaging.camera.dcam_props import DCAMDict
from src.imaging.camera.dcam_types import CheckedDCAMAPI, DCAMException

# DCAMAPI v3.0.301.3690
API = CheckedDCAMAPI()
DCAM_CAPTUREMODE_SNAP = c_int32(0)

if not API.dcam_init(None, byref(c_int32(0)), None):
    raise DCAMException("DCAM initialization failed.")


class Status(IntEnum):
    ERROR = 0
    BUSY = 1
    READY = 3
    UNSTABLE = 4


class Camera:
    TDI_EXPOSURE_TIME = 0.002568533333333333
    AREA_EXPOSURE_TIME = 0.005025378

    IMG_WIDTH = 4096
    IMG_HEIGHT = 64
    # FRAME_Y =
    IMG_BYTES = 524288

    def __init__(self, id_: Literal[0, 1]) -> None:
        self.handle = c_void_p(0)
        API.dcam_open(byref(self.handle), c_int32(id_), None)
        self.properties = DCAMDict.from_dcam(self.handle)

        self.properties["sensor_mode"] = 4  # TDI
        self.properties["sensor_mode_line_bundle_height"] = 128
        API.dcam_precapture(self.handle, DCAM_CAPTUREMODE_SNAP)

    @contextmanager
    def capture(self):
        API.dcam_capture(self.handle)
        yield
        API.dcam_idle(self.handle)

    @contextmanager
    def alloc(self, n_frames: int):
        API.dcam_allocframe(self.handle, c_int32(n_frames))
        yield
        API.dcam_freeframe(self.handle)

    @property
    def status(self) -> Status:
        s = c_ulong(-1)
        API.dcam_getstatus(self.handle, byref(s))
        try:
            return Status(s.value)
        except KeyError:
            raise DCAMException(f"Invalid status. Got {s.value}.")

    @property
    def n_frames_taken(self) -> int:
        """Return number of frames (int) that have been taken."""
        b_index = c_int32(-1)
        f_count = c_int32(-1)
        API.dcam_gettransferinfo(self.handle, byref(b_index), byref(f_count))
        assert b_index != -1
        assert f_count != -1
        return int(f_count.value)

    def get_images(self):
        n = self.n_frames_taken
        addr = c_void_p(0)
        row_bytes = c_int32(0)
        API.dcam_lockdata(self.handle, byref(addr), byref(row_bytes), c_int32(n))
        img = np.ctypeslib.as_array(addr, shape=...)
