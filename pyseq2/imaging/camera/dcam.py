from __future__ import annotations

import os
import pickle
import threading
import time
from concurrent.futures import Future
from concurrent.futures.thread import ThreadPoolExecutor
from contextlib import contextmanager
from ctypes import c_char_p, c_int32, c_uint32, c_void_p, pointer, sizeof
from enum import Enum, IntEnum
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
    overload,
)

import numpy as np
import numpy.typing as npt
from pyseq2.com.thread_mgt import run_in_executor, warn_main_thread
from pyseq2.imaging.camera.dcam_api import DCAM_CAPTURE_MODE
from pyseq2.utils.utils import gen_future

from . import API
from .dcam_api import DCAMException
from .dcam_props import DCAMDict

logger = getLogger(__name__)
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
Cam = Literal[0, 1, 2]
UInt16Array = npt.NDArray[np.uint16]
FourImages = tuple[UInt16Array, UInt16Array, UInt16Array, UInt16Array]


class Mode(Enum):
    """DCAM properties preset"""

    FOCUS_SWEEP = {"sensor_mode": 6, "exposure_time": 0.001, "partial_area_vsize": 5}
    TDI = {"sensor_mode": 4, "sensor_mode_line_bundle_height": 128}


class _Camera:
    IMG_WIDTH = 4096
    BUNDLE_HEIGHT = 128

    def __init__(self, id_: ID) -> None:
        assert id_ in get_args(ID)
        self.id_ = id_

        self.handle = c_void_p(0)
        API.dcam_open(pointer(self.handle), c_int32(id_), None)
        if os.environ.get("FAKE_HISEQ", "0") == "1" or os.name != "nt":
            self.properties = DCAMDict(
                self.handle, pickle.loads((Path(__file__).parent / "saved_props.pk").read_bytes())
            )
        else:
            self.properties = DCAMDict.from_dcam(self.handle)
        self.capture_mode = DCAM_CAPTURE_MODE.SNAP
        logger.info(f"Connected to cam {id_}")

    def initialize(self) -> None:
        ...

    @property
    def capture_mode(self) -> DCAM_CAPTURE_MODE:
        return self._capture_mode

    @capture_mode.setter
    def capture_mode(self, m: DCAM_CAPTURE_MODE) -> None:
        API.dcam_precapture(self.handle, m)
        self._capture_mode = m

    @contextmanager
    def capture(self) -> Generator[None, None, None]:
        API.dcam_capture(self.handle)
        logger.info(f"Cam {self.id_}: Started capturing.")
        try:
            yield
        finally:
            API.dcam_idle(self.handle)
            logger.info(f"Cam {self.id_}: Done capturing.")

    @property
    def status(self) -> Status:
        s = c_int32(-1)
        API.dcam_getstatus(self.handle, pointer(s))
        try:
            return Status(s.value)
        except ValueError:
            raise DCAMException(f"Invalid status. Got {s.value}.")

    @contextmanager
    def attach(self, n_bundles: int, height: int) -> Generator[UInt16Array, None, None]:
        """Generates a numpy array and "attach" it to the camera.
        Aka. Tells the camera to write captured bundles here.

        Args:
            n_bundles (int): Number of bundles
            height (int): Height of each bundle. 128 for TDI. 5 for focus sweep.

        Yields:
            Generator[UInt16Array, None, None]: Output array (n_bundles × height, 4096)
        """
        arr: npt.NDArray[np.uint16] = np.zeros((n_bundles * height, self.IMG_WIDTH), dtype=np.uint16)
        addr, ptr_arr = arr.ctypes.data, (c_void_p * n_bundles)()
        for i in range(n_bundles):
            ptr_arr[i] = 2 * 4096 * height * i + addr

        try:
            API.dcam_attachbuffer(self.handle, ptr_arr, c_uint32(sizeof(ptr_arr)))
            yield arr
        finally:
            API.dcam_releasebuffer(self.handle)

    # @contextmanager
    # def alloc(self, n_bundles: int, height: int) -> Generator[UInt16Array, None, None]:
    #     out: npt.NDArray[np.uint16] = np.empty((n_bundles * height, self.IMG_WIDTH), dtype=np.uint16)
    #     try:
    #         API.dcam_allocframe(self.handle, c_int32(n_bundles))
    #         yield out
    #     finally:
    #         API.dcam_freeframe(self.handle)

    # @contextmanager
    # def _lock_memory(self, height: int, n_curr: int):
    #     addr = pointer((c_uint16 * self.IMG_WIDTH * height)())
    #     row_bytes = c_int32(0)
    #     API.dcam_lockdata(self.handle, pointer(cast(c_void_p, addr)), pointer(row_bytes), c_int32(n_curr))
    #     try:
    #         yield addr
    #     finally:
    #         API.dcam_unlockdata(self.handle)

    # def get_bundle(self, buf: UInt16Array, height: int, n_curr: int) -> None:
    #     with self._lock_memory(height=height, n_curr=n_curr) as addr:
    #         buf[n_curr * height : (n_curr + 1) * height, :] = np.asarray(addr.contents)

    @property
    def n_frames_taken(self) -> int:
        """Return number of frames (int) that have been taken."""
        b_index, f_count = c_int32(-1), c_int32(-1)
        API.dcam_gettransferinfo(self.handle, pointer(b_index), pointer(f_count))
        return f_count.value


T = TypeVar("T", bound=Hashable)
R = TypeVar("R")


class TwoProps(Generic[T, R]):
    """Unified properties of two cameras"""

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
    """Object representing two cameras.
    To access a single camera, index this object.
    `Cam = 0, 1` refers to cameras 0, 1. Whereas 2 refers to both.

    Experiments indicated that dcamapi.dll is not thread-safe."""

    IMG_WIDTH = 4096
    BUNDLE_HEIGHT = 128

    _cams: Future[tuple[_Camera, _Camera]]
    properties: TwoProps

    def __init__(self) -> None:
        self.ready = Future()
        self._executor = ThreadPoolExecutor(max_workers=1)  # Only case of Executor outside COM.
        self._cams = self.post_init()  # self.properties set in here.

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
        self.set_mode("TDI")
        return cams

    def __getitem__(self, id_: ID) -> _Camera:
        return self._cams.result(20)[id_]

    def __getattr__(self, name: str) -> Any:
        if name == "properties":
            logger.info("Waiting for DCAM API to finish initializing. Consider not setting properties now.")
            self._cams.result(60)
            return self.properties
        raise AttributeError

    @run_in_executor
    def initialize(self) -> None:
        [x.initialize() for x in self]

    def n_frames_taken(self, cam: Cam) -> int:
        return min([c.n_frames_taken for c in self]) if cam == 2 else self[cam].n_frames_taken

    @overload
    @contextmanager
    def _attach(
        self, n_bundles: int, height: int, cam: Literal[0, 1] = ...
    ) -> Generator[UInt16Array, None, None]:
        ...

    @overload
    @contextmanager
    def _attach(
        self, n_bundles: int, height: int, cam: Literal[2] = ...
    ) -> Generator[tuple[UInt16Array, UInt16Array], None, None]:
        ...

    @contextmanager
    def _attach(
        self, n_bundles: int, height: int, cam: Cam = 2
    ) -> Generator[UInt16Array, None, None] | Generator[tuple[UInt16Array, UInt16Array], None, None]:
        if cam == 2:
            with self[0].attach(n_bundles, height) as buf1, self[1].attach(n_bundles, height) as buf2:
                logger.debug(f"Allocated memory for {n_bundles} bundles.")
                yield (buf1, buf2)
        else:
            with self[cam].attach(n_bundles, height) as buf1:
                logger.debug(f"Allocated memory for {n_bundles} bundles for cam {cam}.")
                yield buf1

    @property
    def mode(self) -> str:
        return self._mode

    @mode.setter
    def mode(self, m: Literal["TDI", "FOCUS_SWEEP"]) -> None:
        self.set_mode(m)

    def set_mode(self, m: Literal["TDI", "FOCUS_SWEEP"]) -> None:
        self.properties.update(Mode[m].value)
        self._mode = m

    @run_in_executor
    @warn_main_thread
    def capture(
        self,
        n_bundles: int,
        height: int = 128,
        start_attach: Callable[[], Any] = lambda: None,
        fut_capture: Callable[[], Future[Any]] = lambda: gen_future(None),
        mode: Literal["TDI", "FOCUS_SWEEP"] = "TDI",
        cam: Literal[0, 1, 2] = 2,
    ) -> UInt16Array:
        """Captures images and split them into channels.
        Timeout if no bundle was captured within the first 5 seconds.

        Args:
            n_bundles (int): Number of bundles.
            height (int, optional): Height of each bundle. Defaults to 128.
            start_attach (Callable[[], Any], optional): Function to call upon storage attachment. Defaults to lambda:None.
            fut_capture (Callable[[], Future[Any]], optional): Function that produces a Future object that resolves when
                imaging is completed. Used for move commands that return when completed. Defaults to lambda:gen_future(None).
            mode (Literal["TDI", "FOCUS_SWEEP"], optional): Defaults to "TDI".
            cam (Literal[0, 1, 2], optional): Which camera(s) to capture. 2 means both. Defaults to 2.

        Returns:
            UInt16Array: Either (2, n_bundles × height, 2048) or (4, n_bundles × height, 2048).
        """

        def in_ctx():
            fut = fut_capture()
            t0 = time.monotonic()
            while self.n_frames_taken(cam) < n_bundles:
                time.sleep(0.1)
                if taken == 0 and time.monotonic() - t0 > 5:
                    raise Exception(f"Did not capture a single bundle before {5=}s.")
            fut.result()

        self.set_mode(mode)
        with self._attach(n_bundles=n_bundles, height=height, cam=cam) as bufs:
            taken = 0
            start_attach()
            if cam == 2:
                with self[0].capture(), self[1].capture():
                    in_ctx()
            else:
                with self[cam].capture():
                    in_ctx()
            logger.info(f"Retrieved all {n_bundles} bundles.")

        if cam == 2:
            bufs = cast(tuple[UInt16Array, UInt16Array], bufs)
            return cast(UInt16Array, np.hstack(bufs).reshape(-1, 4, 2048).transpose(1, 0, 2))
        bufs = cast(UInt16Array, bufs)
        return cast(UInt16Array, bufs.reshape(-1, 2, 2048).transpose(1, 0, 2))
