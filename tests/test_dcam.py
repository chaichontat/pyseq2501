from ctypes import c_void_p

import pytest

from pyseq2.imaging.camera.dcam import API, TwoProps
from pyseq2.imaging.camera.dcam_api import DCAMException


def test_two_props():
    a, b = {"same": 1, "diff": 0}, {"same": 1, "diff": 1}
    t = TwoProps(a, b)
    with pytest.raises(Exception):
        t["diff"]
    t.update({"diff": 1})
    t["diff"]
    t["same"] = -1
    assert t["same"] == -1


def test_error():
    handle = c_void_p(0)
    with pytest.raises(DCAMException, match="Error code: 5."):
        API.dcam_unlockbits(handle)  # Proxy for return 1.
