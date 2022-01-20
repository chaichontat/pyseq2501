from ctypes import c_char_p, c_int32, c_void_p, pointer

import pytest

from pyseq2.imaging.camera import API
from pyseq2.imaging.camera.dcam import Cameras, TwoProps, _Camera
from pyseq2.imaging.camera.dcam_api import DCAM_CAPTURE_MODE, DCAMException, check_if_failed


def test_camera():
    API.dcam_init(c_void_p(0), pointer(c_int32(0)), c_char_p(0))
    c = _Camera(0)
    assert c.capture_mode == DCAM_CAPTURE_MODE.SNAP
    c.capture_mode = DCAM_CAPTURE_MODE.SEQUENCE
    assert c.capture_mode == DCAM_CAPTURE_MODE.SEQUENCE

    assert c.n_frames_taken == 0

    with c.attach(n_bundles=8, height=128) as buf:
        with c.capture():
            ...


def test_two_props():
    a, b = {"same": 1, "diff": 0}, {"same": 1, "diff": 1}
    t = TwoProps(a, b)
    with pytest.raises(Exception):
        t["diff"]
    t.update({"diff": 1})
    t["diff"]
    t["same"] = -1
    assert t["same"] == -1


# def test_cameras():
#     cs = Cameras()


class Failed:
    @check_if_failed
    def bad(self):
        return 0

    @check_if_failed
    def good(self):
        return 1

    @check_if_failed
    def what(self):
        return "hi"


def test_check_if_failed():
    f = Failed()
    with pytest.raises(DCAMException):
        f.bad()
    with pytest.raises(DCAMException):
        f.what()
    f.good()
