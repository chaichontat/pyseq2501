import math
from contextlib import nullcontext
from typing import Callable, TypeVar

import numpy as np
import pytest
from hypothesis import assume, given
from hypothesis.strategies import SearchStrategy, booleans, composite, floats, integers
from pydantic import ValidationError

from pyseq2.experiment.command import TakeImage
from pyseq2.utils import coords

Ex = TypeVar("Ex", covariant=True)


@composite
def gen_xy(draw: Callable[[SearchStrategy[Ex]], Ex]) -> tuple[float, float]:
    return draw(floats(-5, 30)), draw(floats(-5, 80))


@given(booleans(), integers(int(-6e6), int(6e6)), floats(-1000, 1000))
def test_y(fc: bool, y_start: int, n_bundles: float):
    # Y decreases over movement.
    assume(n_bundles != 0)
    dy = n_bundles * 128 * 0.000375
    y0 = coords.raw_to_mm(fc, y=y_start)
    y1 = y0 + dy

    t = TakeImage.default().copy(update={"xy0": (0, y0), "xy1": (0, y1)})
    nb, ys, _, _ = t.calc_pos(fc)

    assert abs(max(y0, y1) - coords.raw_to_mm(fc, y=ys)) < 0.001
    assert nb == math.ceil(abs(n_bundles))


@given(fc=booleans(), x_start=integers(0, 50000), nx=floats(0, 100), posneg=booleans(), overlap=floats(0, 1))
def test_x(fc: bool, x_start: int, nx: float, posneg: bool, overlap: float):
    dx = nx * 2048 * 0.000375 * (1 - overlap) * (1 if posneg else -1)
    x0 = coords.raw_to_mm(fc, x=x_start)
    x1 = x0 + dx

    cond = overlap != 1
    with nullcontext() if cond else pytest.raises(ValidationError):
        t = TakeImage.default().copy(update={"xy0": (x0, 0), "xy1": (x1, 1), "overlap": overlap})
    if cond:
        return

    _, _, xs, _ = t.calc_pos(fc)

    if nx == 0:
        assert len(xs) == 1
    else:
        assert len(xs) > 1
        assert len(xs) == math.ceil(abs(nx))

    assert min(x_start, coords.mm_to_raw(fc, x=x1)) == xs[0]
    assert min(d := np.diff(xs)) == max(d)


if __name__ == "__main__":
    test_x(True, 0, 0.000001, 0)
