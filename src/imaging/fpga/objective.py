import time
from concurrent.futures import Future
from logging import getLogger

from src.instruments import FPGAControlled, Movable

logger = getLogger(__name__)


Y_OFFSET = int(7e6)


class ObjCmd:
    ...


class Objective(FPGAControlled, Movable):
    ...
