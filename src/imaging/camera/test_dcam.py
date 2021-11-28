import pytest
from src.imaging.camera.dcam_api import DCAM_CAPTURE_MODE, DCAMException, check_if_failed

from .dcam import Cameras, TwoProps, _Camera

# TODO: Make fake DCAM more sophisticated.


def test_camera():
    c = _Camera(0)
    assert c.capture_mode == DCAM_CAPTURE_MODE.SNAP
    c.capture_mode = DCAM_CAPTURE_MODE.SEQUENCE
    assert c.capture_mode == DCAM_CAPTURE_MODE.SEQUENCE

    with pytest.raises(DCAMException):
        c.status

    assert c.n_frames_taken == -1

    with c.alloc(8) as buf:
        with c.capture():
            ...
        for i in range(8):
            c._lock_memory(i)


def test_two_props():
    a, b = {"same": 1, "diff": 0}, {"same": 1, "diff": 1}
    t = TwoProps(a, b)
    with pytest.raises(Exception):
        t["diff"]
    t.update({"diff": 1})
    t["diff"]
    t["same"] = -1
    assert t["same"] == -1


def test_cameras():
    cs = Cameras()


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
        f.what()
    f.good()
