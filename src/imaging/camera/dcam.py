from __future__ import annotations

import os
import pickle
import threading
import time
from concurrent.futures import Future
from concurrent.futures.thread import ThreadPoolExecutor
from contextlib import contextmanager
from ctypes import c_char_p, c_int32, c_uint16, c_void_p, pointer
from enum import Enum, IntEnum
from itertools import chain
from logging import getLogger
from pathlib import Path
from typing import (
    Any,
    Callable,
    Generator,
    Generic,
    Hashable,
    Literal,
    MutableMapping,
    TypeVar,
    cast,
    get_args,
)

import numpy as np
import numpy.typing as npt
from src.imaging.camera.dcam_api import DCAM_CAPTURE_MODE
from src.com.thread_mgt import run_in_executor, warn_main_thread

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
    LIVE_AREA = {"sensor_mode": 1, "contrast_gain": 5}
    TDI = {"sensor_mode": 4, "contrast_gain": 0}


class _Camera:
    # TDI_EXPOSURE_TIME = 0.002568533333333333
    # AREA_EXPOSURE_TIME = 0.005025378

    IMG_WIDTH = 4096
    BUNDLE_HEIGHT = 128

    def __init__(self, id_: ID) -> None:
        assert id_ in get_args(ID)
        self.id_ = id_

        self.handle = c_void_p(0)
        logger.debug(f"Opening cam {id_}")
        API.dcam_open(pointer(self.handle), c_int32(id_), None)
        self._capture_mode = DCAM_CAPTURE_MODE.SNAP
        self.properties["sensor_mode_line_bundle_height"] = 128
        self._mode = Mode.TDI

    @property
    def properties(self) -> DCAMDict:
        if os.environ.get("FAKE_HISEQ", "0") == "1" or os.name != "nt":
            return DCAMDict(
                self.handle, pickle.loads((Path(__file__).parent / "saved_props.pk").read_bytes())
            )
        return DCAMDict.from_dcam(self.handle)

    def initialize(self) -> None:
        ...

    @property
    def capture_mode(self) -> DCAM_CAPTURE_MODE:
        return self._capture_mode

    @capture_mode.setter
    def capture_mode(self, m: DCAM_CAPTURE_MODE):
        API.dcam_precapture(self.handle, m)
        self._capture_mode = m

    @contextmanager
    def capture(self) -> Generator[None, None, None]:
        API.dcam_capture(self.handle)
        try:
            yield
        finally:
            API.dcam_idle(self.handle)

    @contextmanager
    def alloc(self, n_bundles: int, height: int) -> Generator[UInt16Array, None, None]:
        out: npt.NDArray[np.uint16] = np.empty((n_bundles * height, self.IMG_WIDTH), dtype=np.uint16)
        try:
            API.dcam_allocframe(self.handle, c_int32(n_bundles))
            yield out
        finally:
            API.dcam_freeframe(self.handle)

    @contextmanager
    def _lock_memory(self, height: int, n_curr: int):
        addr = pointer((c_uint16 * self.IMG_WIDTH * height)())
        row_bytes = c_int32(0)
        API.dcam_lockdata(self.handle, pointer(cast(c_void_p, addr)), pointer(row_bytes), c_int32(n_curr))
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
        except ValueError:
            raise DCAMException(f"Invalid status. Got {s.value}.")

    # @contextmanager
    # def attach(self, n_bundles: int, arr: npt.NDArray[np.uint16]) -> Generator[None, None, None]:
    #     # TODO Somehow stuck at 4 frames.
    #     addr = arr.ctypes.data
    #     ptr_arr = (c_void_p * n_bundles)()
    #     for i in range(n_bundles):
    #         ptr_arr[i] = 524288 * i + addr
    #     try:
    #         API.dcam_attachbuffer(self.handle, ptr_arr, c_uint32(n_bundles))
    #         yield
    #     finally:
    #         API.dcam_releasebuffer(self.handle)

    @property
    def n_frames_taken(self) -> int:
        """Return number of frames (int) that have been taken."""
        b_index = c_int32(-1)
        f_count = c_int32(-1)
        API.dcam_gettransferinfo(self.handle, pointer(b_index), pointer(f_count))
        return int(f_count.value)

    def get_bundle(self, buf: UInt16Array, height: int, n_curr: int) -> None:
        with self._lock_memory(height=height, n_curr=n_curr) as addr:
            buf[n_curr * height : (n_curr + 1) * height, :] = np.asarray(addr.contents)


T = TypeVar("T", bound=Hashable)
R = TypeVar("R")


class TwoProps(Generic[T, R]):
    def __init__(self, prop1: MutableMapping[T, R], prop2: MutableMapping[T, R]) -> None:
        self._props = (prop1, prop2)

    def __getitem__(self, name: T) -> R:
        a, b = self._props
        if (out := a[name]) != b[name]:
            raise Exception("Value not equal between two props. Check each individually.")
        return out

    def __setitem__(self, name: T, value: R) -> None:
        for p in self._props:
            p[name] = value

    def update(self, to_change: dict[T, R]):
        for k, v in to_change.items():
            self[k] = v


class Cameras:
    """Experiments indicated that dcamapi.dll is not thread-safe."""

    IMG_WIDTH = 4096
    BUNDLE_HEIGHT = 128

    _cams: Future[tuple[_Camera, _Camera]]
    properties: TwoProps

    def __init__(self) -> None:
        self.ready = Future()
        self._executor = ThreadPoolExecutor(max_workers=1)  # Only case of Executor outside COM.
        self._cams = self.post_init()  # self.properties set in here.
        # self._cams.add_done_callback(
        #     lambda _: setattr(self, "properties", TwoProps(*[c.properties for c in self]))
        # )

    @run_in_executor
    @warn_main_thread
    def post_init(self) -> tuple[_Camera, _Camera]:
        t0 = time.monotonic()
        logger.info("Initializing DCAM API.")
        # This is slow that I need to make sure that the thing is still running.
        th = threading.Thread(target=lambda: API.dcam_init(c_void_p(0), pointer(c_int32(0)), c_char_p(0)))
        th.start()
        while th.is_alive():
            time.sleep(2)
            logger.info(f"Still alive. dcam_init takes about 10s. Taken {time.monotonic() - t0:.2f} s.")
        cams = (_Camera(0), _Camera(1))
        self.properties = TwoProps(*[c.properties for c in cams])
        return cams

    def __getitem__(self, id_: ID) -> _Camera:
        return self._cams.result()[id_]

    def __getattr__(self, name: str) -> Any:
        if name == "properties":
            logger.info("Waiting for DCAM API to finish initializing. Consider not setting properties now.")
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
    def _alloc(self, n_bundles: int, height: int) -> Generator[tuple[UInt16Array, UInt16Array], None, None]:
        with self[0].alloc(n_bundles, height) as buf1, self[1].alloc(n_bundles, height) as buf2:
            logger.debug(f"Allocated memory for {n_bundles} bundles.")
            yield (buf1, buf2)

    # @contextmanager
    # def _attach(self, n_bundles: int) -> Generator[tuple[UInt16Array, UInt16Array], None, None]:
    #     # TODO Somehow stuck at 4 frames.
    #     buf1 = np.ones((n_bundles * 128, 4096), dtype=np.uint16)
    #     buf2 = buf1.copy()
    #     assert buf1.ctypes.data != buf2.ctypes.data
    #     with self[0].attach(n_bundles, buf1), self[1].attach(n_bundles, buf2):
    #         logger.debug(f"Allocated memory for {n_bundles} bundles.")
    #         yield (buf1, buf2)

    def _get_bundles(self, bufs: tuple[UInt16Array, UInt16Array], height: int, i: int):
        for c, b in zip(self._cams.result(), bufs):
            c.get_bundle(b, height, i)
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
    @warn_main_thread
    def capture(
        self,
        n_bundles: int,
        start_alloc: Callable[[], Any] = lambda: None,
        start_capture: Callable[[], Any] = lambda: None,
        timeout: float | int = 5,
    ) -> UInt16Array:
        """

        Args:
            n_bundles (int): [description]
            start_alloc (Callable[[], Any], optional): [description]. Defaults to lambda:None.
            start_capture (Callable[[], Any], optional): [description]. Defaults to lambda:None.
            timeout (float, optional): [description]. Defaults to 5.

        Raises:
            Exception: [description]

        Returns:
            UInt16Array: uint16 array with dimension [4, {128*n_bundles}, 2048]
        """
        with self._alloc(n_bundles=n_bundles, height=128) as bufs:
            taken = 0
            start_alloc()
            with self[0].capture(), self[1].capture():
                start_capture()
                t0 = time.monotonic()
                while (avail := self.n_frames_taken) < n_bundles:
                    time.sleep(0.1)
                    if avail > taken:
                        [self._get_bundles(bufs=bufs, height=128, i=i) for i in range(taken, avail)]
                        taken = avail
                    if taken == 0 and time.monotonic() - t0 > timeout:
                        raise Exception(f"Did not capture a single bundle before {timeout=}s.")
            # Done. Retrieve images.
            for i in range(taken, max(avail, n_bundles)):
                self._get_bundles(bufs=bufs, height=128, i=i)
            logger.info(f"Retrieved all {n_bundles} bundles.")

        return cast(UInt16Array, np.flip(np.swapaxes(np.hstack(bufs).reshape(-1, 4, 2048), 1, 0), axis=1))
