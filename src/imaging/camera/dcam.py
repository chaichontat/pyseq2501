from __future__ import annotations

import threading
import time
from concurrent.futures import Future
from concurrent.futures.thread import ThreadPoolExecutor
from contextlib import contextmanager
from ctypes import c_int32, c_uint16, c_void_p, pointer
from enum import Enum, IntEnum
from itertools import chain
from logging import getLogger
from typing import Any, Callable, Generator, Literal, Protocol, cast

import numpy as np
import numpy.typing as npt
from src.imaging.camera.dcam_api import DCAM_CAPTURE_MODE
from src.utils.com import run_in_executor
from src.utils.utils import warn_main_thread

from . import API
from .dcam_api import DCAMException
from .dcam_props import DCAMDict

logger = getLogger("DCAM")
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
FourImages = tuple[UInt16Array, UInt16Array, UInt16Array, UInt16Array]


class Mode(Enum):
    LIVE_AREA = {"sensor_mode": 1, "trigger_source": 1, "contrast_gain": 5}
    TDI = {"sensor_mode": 4, "trigger_source": 2}


class _Camera:
    # TDI_EXPOSURE_TIME = 0.002568533333333333
    # AREA_EXPOSURE_TIME = 0.005025378

    IMG_WIDTH = 4096
    BUNDLE_HEIGHT = 128

    def __init__(self, id_: ID) -> None:
        self.id_ = id_
        self.handle = c_void_p(0)
        logger.debug(f"Opening cam {id_}")
        API.dcam_open(pointer(self.handle), c_int32(id_), None)

        self.properties = DCAMDict.from_dcam(self.handle)
        self._capture_mode = DCAM_CAPTURE_MODE.SNAP
        self.properties["sensor_mode_line_bundle_height"] = 128

    def initialize(self) -> None:
        ...

    @property
    def capture_mode(self) -> DCAM_CAPTURE_MODE:
        return self._capture_mode

    @capture_mode.setter
    def capture_mode(self, m: DCAM_CAPTURE_MODE):
        API.dcam_precapture(self.handle, m)

    @contextmanager
    def capture(self) -> Generator[None, None, None]:
        API.dcam_capture(self.handle)
        try:
            yield
        finally:
            API.dcam_idle(self.handle)

    @contextmanager
    def alloc(self, n_bundles: int) -> Generator[UInt16Array, None, None]:
        out: npt.NDArray[np.uint16] = np.empty(
            (n_bundles * self.BUNDLE_HEIGHT, self.IMG_WIDTH), dtype=np.uint16
        )
        API.dcam_allocframe(self.handle, c_int32(n_bundles))
        # Failed attempt at using attachbuffer.
        # test = np.zeros((n_bundles * self.BUNDLE_HEIGHT, self.IMG_WIDTH), dtype=np.uint16)
        # p = test.ctypes.data
        # API.dcam_attachbuffer(self.handle, pointer(c_void_p(p)), c_uint32(n_bundles))
        try:
            yield out
        finally:
            # API.dcam_releasebuffer(self.handle)
            API.dcam_freeframe(self.handle)

    @contextmanager
    def _lock_memory(self, bundle: int):
        addr = pointer((c_uint16 * self.IMG_WIDTH * self.BUNDLE_HEIGHT)())
        row_bytes = c_int32(0)
        API.dcam_lockdata(self.handle, pointer(cast(c_void_p, addr)), pointer(row_bytes), c_int32(bundle))
        try:
            yield addr
        finally:
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
        return int(f_count.value)

    def get_bundle(self, buf: UInt16Array, n_curr: int) -> None:
        with self._lock_memory(n_curr) as addr:
            buf[n_curr * self.BUNDLE_HEIGHT : (n_curr + 1) * self.BUNDLE_HEIGHT, :] = np.asarray(
                addr.contents
            )


class GetSetable(Protocol):
    def __getitem__(self, name: Any) -> Any:
        ...

    def __setitem__(self, name: Any, value: Any) -> None:
        ...


class TwoProps:
    def __init__(self, prop1: GetSetable, prop2: GetSetable) -> None:
        self._props = (prop1, prop2)

    def __getitem__(self, name: str) -> Any:
        a, b = self._props
        if (out := a[name]) != b[name]:
            raise Exception("Value not equal between two props. Check each individually.")
        return out

    def __setitem__(self, name: str, value: Any) -> None:
        for p in self._props:
            p[name] = value

    def update(self, to_change: dict[str, Any]):
        for k, v in to_change.items():
            self[k] = v


class Cameras:
    """Experiments indicated that dcamapi.dll is not thread-safe."""

    IMG_WIDTH = 4096
    BUNDLE_HEIGHT = 128

    _cams: Future[tuple[_Camera, _Camera]]
    properties: TwoProps

    def __init__(self) -> None:
        self._executor = ThreadPoolExecutor(max_workers=1)
        self._cams = self.post_init()
        self._cams.add_done_callback(
            lambda _: setattr(self, "properties", TwoProps(*[c.properties for c in self]))
        )

    @run_in_executor
    def post_init(self) -> tuple[_Camera, _Camera]:
        if threading.current_thread() is threading.main_thread():
            logger.warning("Running on mainthread.")
        t0 = time.time()
        logger.debug("Initializing DCAM API.")
        # This is slow that I need to make sure that the thing is still running.
        th = threading.Thread(target=lambda: API.dcam_init(None, pointer(c_void_p(0)), None))
        th.start()
        while th.is_alive():
            time.sleep(2)
            logger.debug(f"Still alive. dcam_init takes about 10s. Taken {time.time() - t0:.2f} s.")
        return (_Camera(0), _Camera(1))

    def __getitem__(self, id_: ID) -> _Camera:
        return self._cams.result()[id_]

    def __getattr__(self, name: str) -> Any:
        if name == "properties":
            logger.warning(
                "Waiting for DCAM API to finish initializing. Consider not setting properties now."
            )
            self._cams.result()
            return self.properties
        raise AttributeError

    @run_in_executor
    def initialize(self) -> None:
        [x.initialize() for x in self]
        self.mode = Mode.TDI

    @property
    def n_frames_taken(self) -> int:
        return min([c.n_frames_taken for c in self])

    @contextmanager
    def _alloc(self, n_bundles: int) -> Generator[tuple[UInt16Array, UInt16Array], None, None]:
        with self[0].alloc(n_bundles) as buf1, self[1].alloc(n_bundles) as buf2:
            logger.debug(f"Allocated memory for {n_bundles} bundles.")
            yield (buf1, buf2)

    def _get_bundles(self, bufs: tuple[UInt16Array, UInt16Array], i: int):
        for c, b in zip(self._cams.result(), bufs):
            c.get_bundle(b, i)
        if i == 0 or i % 5 == 0:
            logger.info(f"Retrieved bundle {i + 1}.")

    @property
    def mode(self):
        return self._mode

    @mode.setter
    def mode(self, m: Mode) -> None:
        self.properties.update(m.value)
        self._mode = m

    @run_in_executor
    @warn_main_thread(logger)
    def capture(
        self,
        n_bundles: int,
        start_alloc: Callable[[], Any] = lambda: None,
        start_capture: Callable[[], Any] = lambda: None,
        polling_time: float | int = 0.1,
        timeout: float | int = 5,
    ) -> FourImages:
        with self._alloc(n_bundles) as bufs:
            taken = 0
            start_alloc()
            with self[0].capture(), self[1].capture():
                start_capture()
                t0 = time.time()
                while (avail := self.n_frames_taken) < n_bundles:
                    time.sleep(polling_time)
                    if avail > taken:
                        [self._get_bundles(bufs, i) for i in range(taken, avail)]
                        taken = avail
                    if taken == 0 and time.time() - t0 > timeout:
                        raise Exception(f"Did not capture a single bundle before {timeout=}s.")
            # Done. Retrieve images.
            for i in range(taken, max(avail, n_bundles)):
                self._get_bundles(bufs, i)
            logger.info(f"Retrieved bundle {n_bundles}.")
        return cast(FourImages, (*chain(*(((x[:, :2048], x[:, 2048:]) for x in bufs))),))
