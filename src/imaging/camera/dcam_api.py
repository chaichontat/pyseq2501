import os
import time
from ctypes import c_int32, pointer
from enum import IntEnum
from functools import wraps
from logging import getLogger
from typing import Callable, ParamSpec, TypeVar

P = ParamSpec("P")
R = TypeVar("R")

if os.name == "nt":
    from ctypes import WinDLL
else:

    class WinDLL:
        def __init__(self, _: str) -> None:
            ...

        def __getattribute__(self, __name: str) -> Callable[P, bool]:
            if __name.startswith("dcam"):
                t = 2 if __name == "dcam_init" else 0.05

                def fake_func(*_: P.args, **__: P.kwargs) -> bool:
                    time.sleep(t)
                    return True

                return fake_func
            return super().__getattribute__(__name)


DCAM_DEFAULT_ARG = c_int32(0)
DCAM_DEFAULT_ARG_p = pointer(DCAM_DEFAULT_ARG)
logger = getLogger("DCAMAPI")


IGNORE = {
    "dcam_getpropertyname",
    "dcam_getpropertyattr",
    "dcam_getpropertyvalue",
    "dcam_getpropertyvaluetext",
    "dcam_getnextpropertyid",
    "dcam_querypropertyvalue",
}


def check_if_failed(f: Callable[P, R]) -> Callable[P, R]:
    @wraps(f)
    def wrapper(*args: P.args, **kwargs: P.kwargs) -> R:
        res = f(*args, **kwargs)
        # Literally the only function that returns int32 instead of BOOL.
        if res != 1 and f.__name__ != "dcam_getlasterror":
            raise DCAMReturnedZero(f"{f.__name__} did not return NOERR.")
        if f.__name__ not in IGNORE:
            logger.debug(f"{f.__name__} [green]OK")
        return res

    return wrapper


class DCAMAPI(WinDLL):
    def __init__(self) -> None:
        super().__init__("dcamapi.dll")


class CheckedDCAMAPI(DCAMAPI):
    def __getitem__(self, name: str) -> Callable[..., bool]:
        return check_if_failed(super().__getitem__(name))  # type: ignore


class DCAMException(Exception):
    ...


class DCAMReturnedZero(DCAMException):
    ...


class DCAM_CAPTURE_MODE(IntEnum):
    SNAP = 0
    SEQUENCE = 1

    def __str__(self) -> str:
        return str(self.value)
