from typing import Literal, Optional, overload

Y_UPPER = -180000
A_LEFT = 7331
B_LEFT = 33070
X_STEP_MM = 409.6
Y_STEP_MM = 1e5


@overload
def raw_to_mm(flowcell: Literal[0, 1], *, x: int, y: None = None) -> float:
    ...


@overload
def raw_to_mm(flowcell: Literal[0, 1], *, y: int, x: None = None) -> float:
    ...


@overload
def raw_to_mm(flowcell: Literal[0, 1], *, x: int, y: int) -> tuple[float, float]:
    ...


@overload
def raw_to_mm(flowcell: Literal[0, 1], *, x: None = None, y: None = None) -> None:
    ...


def raw_to_mm(
    flowcell: Literal[0, 1], x: Optional[int] = None, y: Optional[int] = None
) -> None | tuple[float, float] | float:
    x_offset = B_LEFT if flowcell else A_LEFT

    if x is not None and y is not None:
        return ((x - x_offset) / X_STEP_MM, (y - Y_UPPER) / Y_STEP_MM)
    if x is not None:
        return (x - x_offset) / X_STEP_MM
    if y is not None:
        return (y - Y_UPPER) / Y_STEP_MM
    return None


@overload
def mm_to_raw(flowcell: Literal[0, 1], *, x: float, y: None = None) -> int:
    ...


@overload
def mm_to_raw(flowcell: Literal[0, 1], *, y: float, x: None = None) -> int:
    ...


@overload
def mm_to_raw(flowcell: Literal[0, 1], *, x: float, y: float) -> tuple[int, int]:
    ...


@overload
def mm_to_raw(flowcell: Literal[0, 1], *, x: None = None, y: None = None) -> None:
    ...


def mm_to_raw(
    flowcell: Literal[0, 1], *, x: Optional[float] = None, y: Optional[float] = None
) -> None | int | tuple[int, int]:
    x_offset = B_LEFT if flowcell else A_LEFT

    if x is not None and y is not None:
        return (int(x * X_STEP_MM + x_offset), int(y * Y_STEP_MM + Y_UPPER))
    if x is not None:
        return int(x * X_STEP_MM + x_offset)
    if y is not None:
        return int(y * Y_STEP_MM + Y_UPPER)
    return None
