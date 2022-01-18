from __future__ import annotations

import re
from math import ceil
from typing import (
    Any,
    Callable,
    Dict,
    Literal,
    Optional,
    ParamSpec,
    Sequence,
    Tuple,
    TypedDict,
    TypeVar,
    cast,
    overload,
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


class InvalidResponse(Exception):
    ...


def ok_if_match(expected: Sequence[str] | str, exception_on_fail: bool = True) -> Callable[[str], bool]:
    def wrapped(resp: str) -> bool:
        if isinstance(expected, Sequence) and resp in expected:
            return True
        if resp == expected:
            return True
        if exception_on_fail:
            raise InvalidResponse(f"Got {resp}, expected {expected}.")
        return False

    return wrapped


def check_none(x: T | None) -> T:
    if x is None:
        raise InvalidResponse()
    return x


def ok_re(target: str, f: Callable[..., T] = bool) -> Callable[[str], T]:
    """f is your responsibility."""
    r = re.compile(target)

    def inner(resp: str) -> T:
        match = r.search(resp)
        if match is None:
            raise InvalidResponse(f"Got {resp}, expected to match {target}.")
        if r.groups < 2:
            return f(match.group(r.groups))
        return f(*(match.group(i) for i in range(1, r.groups + 1)))

    return inner


def chkrng(f: Callable[P, T], min_: int | float, max_: int | float) -> Callable[P, T]:
    """Check the (x := first argument) of a function if min_ <= x <= max."""

    def wrapper(*args: P.args, **kwargs: P.kwargs) -> T:
        x = cast(int | float, args[0])
        if not (min_ <= x <= max_):
            raise ValueError(f"Invalid value for {f.__name__}: Got {x}. Expected [{min_}, {max_}].")
        return f(*args, **kwargs)

    return wrapper


@overload
def λ_int(λ: Callable[[Any, Any], T]) -> Callable[[int, int], T]:
    ...


@overload
def λ_int(λ: Callable[[Any], T]) -> Callable[[int], T]:
    ...


def λ_int(λ: Callable[[Any], T] | Callable[[Any, Any], T]) -> Callable[[int], T] | Callable[[int, int], T]:
    def inner(*args: int) -> T:
        return λ(*args)

    return inner


IntFloat = int | float


@overload
def λ_float(λ: Callable[[Any, Any], T]) -> Callable[[IntFloat, IntFloat], T]:
    ...


@overload
def λ_float(λ: Callable[[Any], T]) -> Callable[[IntFloat], T]:
    ...


def λ_float(
    λ: Callable[[Any], T] | Callable[[Any, Any], T]
) -> Callable[[IntFloat], T] | Callable[[IntFloat, IntFloat], T]:
    def inner(*args: IntFloat) -> T:
        return λ(*args)

    return inner


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
