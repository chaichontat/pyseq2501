from __future__ import annotations

import threading
from concurrent.futures import Future, ThreadPoolExecutor
from functools import wraps
from math import ceil
from typing import (
    Any,
    Callable,
    Dict,
    Literal,
    Optional,
    ParamSpec,
    Protocol,
    Tuple,
    TypedDict,
    TypeVar,
    cast,
)

TILE_WIDTH = 0.769  # mm
RESOLUTION = 0.375  # µm / px
BUNDLE_HEIGHT = 128  # Height of sensor
NYQUIST_OBJ = 235  # Nyquist dist in objective steps

FlowCell = Literal["A", "B"]
FLOWCELL_ORIGIN: Dict[FlowCell, Tuple[int, int]] = {
    "A": (17571, -180000),
    "B": (43310, -180000),
}

# TODO: Move this
X_SPUM = 0.4096
Y_SPUM = 100

T, P = TypeVar("T"), ParamSpec("P")


def gen_future(x: T) -> Future[T]:
    fut = Future()
    fut.set_result(x)
    return fut


class Threaded(Protocol):
    _executor: ThreadPoolExecutor


# TODO Wait until mypy supports ParamSpec.
def run_in_executor(f: Callable[P, T]) -> Callable[P, Future[T]]:
    """
    Prevents a race condition in which a result from the running object is dependent on an object in the queue.
    """

    @wraps(f)
    def inner(self: Threaded, *args: Any, **kwargs: Any) -> Future[T]:
        if threading.current_thread() not in self._executor._threads:
            return cast(Future[T], self._executor.submit(lambda: f(self, *args, **kwargs)))  # type: ignore
        else:
            future: Future[T] = Future()
            future.set_result(f(self, *args, **kwargs))  # type: ignore
            return future

    return inner


class FakeLogger:
    """To avoid `if logger is None` from appearing everywhere."""

    def debug(self, _: str) -> None:
        ...

    def warning(self, _: str) -> None:
        ...

    def error(self, _: str) -> None:
        ...


class Pos(TypedDict):
    x_center: int
    y_center: int
    x_initial: int
    y_initial: int
    x_final: int
    y_final: int
    n_tiles: int
    n_frames: int
    obj_pos: Optional[int]


def position(flow_cell: FlowCell, box, overlap=0) -> Pos:
    """Returns stage position information.

    The center of the image is used to bring the section into focus
    and optimize laser intensities. Image scans of sections start on
    the upper right corner of the section. The section is imaged in
    strips 0.760 mm wide by length of the section long until the entire
    section has been imaged. The box region of interest surrounding the
    section is converted into stage and imaging details to scan the
    entire section.

    =========  ==============================================
        key      description
    =========  ==============================================
    x_center   The xstage center position of the section.
    y_center   The ystage center position of the section.
    x_initial  Initial xstage position to scan the section.
    y_initial  Initial ystage position to scan the section.
    x_final    Last xstage position of the section scan
    y_final    Last ystage position of the section scan
    n_tiles    Number of tiles to scan the entire section.
    n_frames   Number of frames to scan the entire section.
    =========  ==============================================

    **Parameters:**
    - AorB (str): Flowcell A or B.
    - box ([float, float, float, float]) = The region of interest as
        x&y position of the corners of a box surrounding the section
        to be imaged defined as [LLx, LLy, URx, URy] where LL=Lower
        Left and UR=Upper Right corner using the slide ruler.

    **Returns:**
    - dict: Dictionary of stage positioning and imaging details to scan
        the entire section. See table above for details.
    """

    LLx = box[0]
    LLy = box[1]
    URx = box[2]
    URy = box[3]

    # Number of scans
    dx = TILE_WIDTH - RESOLUTION * overlap / 1000  # x stage delta in in mm
    n_tiles = ceil((LLx - URx) / dx)

    # X center of scan
    x_center = FLOWCELL_ORIGIN[flow_cell][0]
    x_center -= LLx * 1000 * X_SPUM
    x_center += (LLx - URx) * 1000 / 2 * X_SPUM
    x_center = int(x_center)

    # initial X of scan
    x_initial = n_tiles * dx * 1000 / 2  # 1/2 fov width in microns
    # if self.overlap_dir == "left":
    x_initial -= RESOLUTION * overlap  # Move stage to compensate for discarded initial px
    x_initial = int(x_center - x_initial * X_SPUM)

    # initial Y of scan
    y_initial = int(FLOWCELL_ORIGIN[flow_cell][1] + LLy * 1000 * Y_SPUM)

    # Y center of scan
    y_length = (LLy - URy) * 1000
    y_center = y_initial - y_length / 2 * Y_SPUM
    y_center = int(y_center)

    # Number of frames
    n_frames = y_length / BUNDLE_HEIGHT / RESOLUTION

    # Adjust x and y center so focus will image (32 frames, 128 bundle) in center of section
    x_center -= int(TILE_WIDTH * 1000 * X_SPUM / 2)
    y_center += int(32 * BUNDLE_HEIGHT / 2 * RESOLUTION * Y_SPUM)

    # Calculate final x & y stage positions of scan

    return Pos(
        x_center=x_center,
        y_center=y_center,
        x_initial=x_initial,
        y_initial=y_initial,
        x_final=int(x_initial + (LLx - URx) * 1000 * X_SPUM),
        y_final=int(y_initial - y_length * Y_SPUM),
        n_tiles=n_tiles,
        n_frames=ceil(n_frames + 10),
        obj_pos=None,
    )
