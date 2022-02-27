import pytest

from pyseq2.imaging.camera.dcam import TwoProps
from pyseq2.imaging.camera.dcam_api import DCAM_CAPTURE_MODE, DCAMException, check_if_failed


def test_two_props():
    a, b = {"same": 1, "diff": 0}, {"same": 1, "diff": 1}
    t = TwoProps(a, b)
    with pytest.raises(Exception):
        t["diff"]
    t.update({"diff": 1})
    t["diff"]
    t["same"] = -1
    assert t["same"] == -1
