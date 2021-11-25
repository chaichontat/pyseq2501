from ctypes import WinDLL
from functools import wraps
from typing import Any


class DCAMAPI(WinDLL):
    def __init__(self) -> None:
        super().__init__("dcamapi.dll")
