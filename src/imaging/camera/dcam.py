from concurrent.futures.thread import ThreadPoolExecutor
from contextlib import contextmanager
from ctypes import c_int32, c_uint16, c_void_p, pointer
from enum import IntEnum
from itertools import chain
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


class SensorMode(IntEnum):
    AREA = 1
    LINE = 3
    TDI = 4
    PARTIAL_AREA = 6


ID = Literal[0, 1]
UInt16Array = npt.NDArray[np.uint16]


class _Camera:
    TDI_EXPOSURE_TIME = 0.002568533333333333
    AREA_EXPOSURE_TIME = 0.005025378

    IMG_WIDTH = 4096
    BUNDLE_HEIGHT = 128

    def __init__(self, id_: ID) -> None:
        self.id_ = id_
        self.handle = c_void_p(0)
        API.dcam_open(pointer(self.handle), c_int32(id_), None)
        self.properties = DCAMDict.from_dcam(self.handle)
        self.initialize()

    def initialize(self) -> None:
        self.sensor_mode = SensorMode.TDI
        API.dcam_precapture(self.handle, DCAM_CAPTURE_MODE.SNAP)

    @property
    def sensor_mode(self):
        return self.properties["sensor_mode"]

    @sensor_mode.setter
    def sensor_mode(self, m: SensorMode):
        if m == self.sensor_mode:
            return
        self.properties["sensor_mode"] = m.value
        self.properties["sensor_mode_line_bundle_height"] = 128 if m == SensorMode.TDI else 64

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
    def get_images(self, n_bundles: int, split: Literal[True] = ...) -> tuple[UInt16Array, UInt16Array]:
        ...

    @overload
    def get_images(self, n_bundles: int, split: Literal[False] = ...) -> UInt16Array:
        ...

    def get_images(self, n_bundles: int, split: bool = True) -> UInt16Array | tuple[UInt16Array, UInt16Array]:
        out: npt.NDArray[np.uint16] = np.empty(
            (n_bundles * self.BUNDLE_HEIGHT, self.BUNDLE_HEIGHT), dtype=np.uint16
        )

        for i in range(n_bundles):
            with self._lock_memory(i) as addr:
                out[i * self.BUNDLE_HEIGHT : (i + 1) * self.BUNDLE_HEIGHT, :] = np.asarray(addr.contents)

        if split:
            half = int(self.IMG_WIDTH / 2)
            return (out[:, :half], out[:, half:])
        return out

    # def getModelInfo(self, camera_id):
    #     c_buf_len = 20
    #     c_buf = ctypes.create_string_buffer(c_buf_len)
    #     dcam.dcam_getmodelinfo(
    #         c_int32(camera_id), c_int32(DCAM_IDSTR_MODEL), c_buf, c_int(c_buf_len)
    #     )
    #     return c_buf.value


class Cameras:
    """Experiments indicated that dcamapi.dll is not thread-safe."""

    IMG_WIDTH = 4096
    BUNDLE_HEIGHT = 128

    _cams: tuple[_Camera, _Camera]

    def __getitem__(self, id_: ID) -> _Camera:
        return self._cams[id_]

    def __init__(self) -> None:
        self._executor = ThreadPoolExecutor(max_workers=1)
        self.post_init()

    @run_in_executor
    def post_init(self):
        API.dcam_init(None, pointer(c_void_p(0)), None)
        self._cams = (_Camera(0), _Camera(1))

    @run_in_executor
    def initialize(self) -> None:
        [x.initialize() for x in self]

    @property
    def sensor_mode(self) -> SensorMode:
        assert self[0].sensor_mode == self[1].sensor_mode
        return SensorMode(int(self[0].sensor_mode))

    @sensor_mode.setter
    def sensor_mode(self, m: SensorMode):
        self[0].sensor_mode = m
        self[1].sensor_mode = m

    def status(self) -> None:
        return

    @contextmanager
    def alloc(self, n_bundles: int) -> Generator[None, None, None]:
        with self[0]._alloc(n_bundles), self[1]._alloc(n_bundles):
            yield

    @contextmanager
    def capture(self) -> Generator[None, None, None]:
        with self[0]._capture(), self[1]._capture():
            yield

    @run_in_executor
    def get_images(self, n_bundles: int) -> tuple[UInt16Array, ...]:
        # Flatten list.
        return (*chain(*[x.get_images(n_bundles) for x in self]),)
