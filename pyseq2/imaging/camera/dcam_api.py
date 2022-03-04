import os
import threading
from ctypes import c_int32, pointer
from enum import IntEnum
from functools import wraps
from logging import getLogger
from typing import Callable, ParamSpec, TypeVar

from pyseq2.utils.utils import IS_FAKE

P = ParamSpec("P")
R = TypeVar("R")

if not IS_FAKE():
    from ctypes import WinDLL

    # Ignore because in Windows, Pylance would complain that WinDLL is not a base class.
    class DCAMAPI(WinDLL):  # type: ignore
        def __init__(self) -> None:
            super().__init__("dcamapi.dll")

else:
    from .fake_dcam import FakeAPI as DCAMAPI


DCAM_DEFAULT_ARG = c_int32(0)
DCAM_DEFAULT_ARG_p = pointer(DCAM_DEFAULT_ARG)
logger = getLogger(__name__)
LOCK = threading.Lock()


IGNORE = {
    "dcam_getpropertyname",
    "dcam_getpropertyattr",
    "dcam_getpropertyvalue",
    "dcam_getpropertyvaluetext",
    "dcam_getnextpropertyid",
    "dcam_querypropertyvalue",
}


def check_if_failed(f: Callable[P, R]) -> Callable[P, R]:
    """Raise Exception if calls did not return 1."""

    @wraps(f)
    def wrapper(*args: P.args, **kwargs: P.kwargs) -> R:
        with LOCK:
            res = f(*args, **kwargs)
        # Literally the only function that returns int32 instead of BOOL.
        if res != 1 and f.__name__ != "dcam_getlasterror":
            raise DCAMReturnedZero(f"{f.__name__} did not return NOERR.")

        if f.__name__ not in IGNORE:
            logger.debug(f"{f.__name__} [green]OK")
        return res

    return wrapper


class CheckedDCAMAPI(DCAMAPI):  # type: ignore
    def __getitem__(self, name: str) -> Callable[..., bool]:
        f: Callable[..., bool] = super().__getitem__(name)
        return check_if_failed(f)


class DCAMException(Exception):
    ...


class DCAMReturnedZero(DCAMException):
    ...


class DCAM_CAPTURE_MODE(IntEnum):
    SNAP = 0
    SEQUENCE = 1

    def __str__(self) -> str:
        return str(self.value)
