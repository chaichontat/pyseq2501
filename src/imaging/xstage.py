from __future__ import annotations

import logging
from concurrent.futures import Future
from contextlib import contextmanager

from src.instruments import Movable, UsesSerial
from src.utils.com import COM, CmdVerify, Command, is_between

logger = logging.getLogger(__name__)


class XStage(UsesSerial, Movable):
    HOME = 30000
    RANGE = (1000, 50000)
    STEPS_PER_UM = 0.4096

    @property
    def position(self) -> Future:
        ...
