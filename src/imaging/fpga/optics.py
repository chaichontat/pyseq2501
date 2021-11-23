import time
from concurrent.futures import Future
from logging import getLogger
from typing import Callable, ClassVar, TypedDict

from src.instruments import FPGAControlled

logger = getLogger("optics")

ID = Literal[1, 2]


class OpticCmd:
    EM_FILTER_IN = "EM2I"
    EM_FILTER_OUT = "EM2O"
    HOME: Callable[[ID], str] = lambda i: f"EX{i}HM"
    SET_OD: Callable[[ID, int], str] = lambda i, x: f"EX{i}MV {x}"


class Optics(FPGAControlled):
    ...


from typing import Dict, Literal, Set

OD_GREEN = Literal["OPEN", "1.0", "2.0", "3.5", "3.8", "4.0", "4.5", "CLOSED"]
OD_RED = Literal["OPEN", "0.2", "0.5", "0.6", "1.0", "2.4", "4.0", "CLOSED"]


# OD: dict[ID, Set[] = {
#     1: {"OPEN", "1.0", "2.0", "3.5", "3.8", "4.0", "4.5", "CLOSED"},
#     2: {"OPEN", "0.2", "0.5", "0.6", "1.0", "2.4", "4.0", "CLOSED"},
# }
