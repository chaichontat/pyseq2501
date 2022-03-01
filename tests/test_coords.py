from hypothesis import given
from hypothesis.strategies import booleans, floats, integers

from pyseq2.utils.coords import mm_to_raw, raw_to_mm


@given(booleans(), integers(0, 50000), integers(-6000000, 6000000))
def test_coords1(flowcell: bool, x: int, y: int):
    mx, my = raw_to_mm(flowcell, x=x, y=y)
    nx, ny = mm_to_raw(flowcell, x=mx, y=my)
    assert abs(x - nx) < 3
    assert abs(y - ny) < 3


@given(booleans(), floats(-5, 30), floats(-5, 80))
def test_coords2(flowcell: bool, x: int, y: int):
    nx, ny = mm_to_raw(flowcell, x=x, y=y)
    mx, my = raw_to_mm(flowcell, x=nx, y=ny)
    assert abs(x - mx) < 0.01
    assert abs(y - my) < 0.01
