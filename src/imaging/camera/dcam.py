from concurrent.futures.thread import ThreadPoolExecutor
from contextlib import contextmanager
from ctypes import c_int32, c_uint16, c_void_p, pointer
from enum import IntEnum
from typing import Generator, Literal, cast, overload

import numpy as np
import numpy.typing as npt
from src.imaging.camera.dcam_api import DCAM_CAPTURE_MODE
from src.utils.com import run_in_executor

from . import API
from .dcam_api import DCAMException
from .dcam_props import DCAMDict

# DCAMAPI v3.0.301.3690


class Status(IntEnum):
    """dcamapi.h line 231"""

    ERROR = 0
    BUSY = 1
    READY = 2
    STABLE = 3
    UNSTABLE = 4


ID = Literal[0, 1]
UInt16Array = npt.NDArray[np.uint16]


class Camera:
    TDI_EXPOSURE_TIME = 0.002568533333333333
    AREA_EXPOSURE_TIME = 0.005025378

    IMG_WIDTH = 4096
    BUNDLE_HEIGHT = 128
    # FRAME_Y =
    # IMG_BYTES = IMG_WIDTH * BUNDLE_HEIGHT / 2

    def __init__(self, id_: ID) -> None:
        self.id_ = id_
        self.initialize()

    def initialize(self) -> None:
        self.handle = c_void_p(0)
        API.dcam_open(pointer(self.handle), c_int32(self.id_), None)
        self.properties = DCAMDict.from_dcam(self.handle)

        self.properties["sensor_mode"] = 4  # TDI
        self.properties["sensor_mode_line_bundle_height"] = self.BUNDLE_HEIGHT
        API.dcam_precapture(self.handle, DCAM_CAPTURE_MODE.SNAP)

    @contextmanager
    def _capture(self) -> Generator[None, None, None]:
        API.dcam_capture(self.handle)
        yield
        API.dcam_idle(self.handle)

    @contextmanager
    def _alloc(self, n_bundles: int) -> Generator[None, None, None]:
        API.dcam_allocframe(self.handle, c_int32(n_bundles))
        yield
        API.dcam_freeframe(self.handle)

    @contextmanager
    def _lock_memory(self, bundle: int):
        addr = pointer((c_uint16 * self.IMG_WIDTH * self.BUNDLE_HEIGHT)())
        row_bytes = c_int32(0)
        API.dcam_lockdata(
            self.handle,
            pointer(cast(c_void_p, addr)),
            pointer(row_bytes),
            c_int32(bundle),
        )
        yield addr
        API.dcam_unlockdata(self.handle)

    # def capture(self, n_frames: int):
    #     # call FPGA
    #     with self._alloc(n_frames):
    #         # Send laser open
    #         # Move
    #         with self._capture():
    #             ...  # while moving not done or calculate translation time.
    #         # Check frame count
    #     # Reset Y

    @property
    def status(self) -> Status:
        s = c_int32(-1)
        API.dcam_getstatus(self.handle, pointer(s))
        try:
            return Status(s.value)
        except KeyError:
            raise DCAMException(f"Invalid status. Got {s.value}.")

    @property
    def n_frames_taken(self) -> int:
        """Return number of frames (int) that have been taken."""
        b_index = c_int32(-1)
        f_count = c_int32(-1)
        API.dcam_gettransferinfo(self.handle, pointer(b_index), pointer(f_count))
        assert b_index.value != -1
        assert f_count.value != -1
        return int(f_count.value)

    @overload
    @run_in_executor
    def get_images(self, n: int, split: bool = True) -> tuple[UInt16Array, UInt16Array]:
        ...

    @overload
    @run_in_executor
    def get_images(self, n: int, split: bool = False) -> UInt16Array:
        ...

    @run_in_executor
    def get_images(self, n_bundles: int, split: bool = True) -> UInt16Array | tuple[UInt16Array, UInt16Array]:
        out = np.empty((n_bundles * self.BUNDLE_HEIGHT, self.BUNDLE_HEIGHT), dtype=np.uint16)

        for i in range(n_bundles):
            with self._lock_memory(i) as addr:
                out[i * self.BUNDLE_HEIGHT : (i + 1) * self.BUNDLE_HEIGHT, :] = np.asarray(addr.contents)

        if split:
            half = int(self.IMG_WIDTH / 2)
            return (out[:, :half], out[:, half:])
        return out


class Cameras:
    """Running two cameras simultaneously crashes the cameras, necessitating a HiSeq hard reset."""

    BUNDLE_HEIGHT = 128
    IMG_WIDTH = 4096
    BUNDLE_HEIGHT = 128

    g: Camera
    r: Camera

    def __init__(self) -> None:
        self._executor = ThreadPoolExecutor(max_workers=1)
        self.g, self.r = Camera(0), Camera(1)
        self.initialize()

    @run_in_executor
    def initialize(self) -> None:
        self.g.initialize()
        return self.r.initialize()

    @contextmanager
    def alloc(self, n_bundles: int):
        with self.g._alloc(n_bundles), self.r._alloc(n_bundles):
            yield

    @contextmanager
    def capture(self):
        with self.g._capture(), self.r._capture():
            yield

    @run_in_executor
    def get_images(self, n_bundles: int):
        g = self.g.get_images(n_bundles)
        r = self.r.get_images(n_bundles)
        return (*(g.result()), *r.result())
