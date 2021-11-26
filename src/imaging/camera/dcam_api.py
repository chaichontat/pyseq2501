import os
from ctypes import cast
from enum import IntEnum
from functools import wraps
from logging import getLogger
from typing import Any, Callable, ParamSpec, TypeVar

if os.name == "nt":
    from ctypes import WinDLL
else:

    class WinDLL:
        def __init__(self, _: str) -> None:
            ...

        def __getitem__(self, _: str) -> Any:
            def fake_func(*_, **__) -> bool:
                return True

            return fake_func


logger = getLogger("DCAMAPI")


IGNORE = {
    "dcam_getpropertyname",
    "dcam_getpropertyattr",
    "dcam_getpropertyvalue",
    "dcam_getpropertyvaluetext",
    "dcam_getnextpropertyid",
    "dcam_querypropertyvalue",
}

P = ParamSpec("P")
R = TypeVar("R")


def check_if_failed(f: Callable[P, R]) -> Callable[P, R]:
    @wraps(f)
    def wrapper(*args: P.args, **kwargs: P.kwargs) -> R:
        res = f(*args, **kwargs)
        # Literally the only function that returns int32 instead of BOOL.
        if res == 0 and f.__name__ != "dcam_getlasterror":
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
        return check_if_failed(super().__getitem__(name))


class DCAMException(Exception):
    ...


class DCAMReturnedZero(DCAMException):
    ...


class DCAM_CAPTURE_MODE(IntEnum):
    SNAP = 0
    SEQUENCE = 1

    def __str__(self) -> str:
        return str(self.value)
