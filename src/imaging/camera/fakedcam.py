import time
from concurrent.futures import ThreadPoolExecutor
from contextlib import contextmanager
from typing import Generator

import numpy as np
from src.imaging.camera.dcam import Cameras
from src.utils.utils import run_in_executor


class FakeCameras(Cameras):
    TDI_EXPOSURE_TIME = 0.002568533333333333
    AREA_EXPOSURE_TIME = 0.005025378

    IMG_WIDTH = 4096
    IMG_HEIGHT = 128

    def __init__(self) -> None:
        self._executor = ThreadPoolExecutor(max_workers=1)
        self._n_bundles = 0

    @run_in_executor
    def initialize(self) -> None:
        return time.sleep(1)

    @contextmanager
    def alloc(self, n_bundles: int) -> Generator[None, None, None]:
        self._n_bundles = n_bundles
        yield

    @contextmanager
    def capture(self) -> Generator[None, None, None]:
        yield

    @run_in_executor
    def get_images(self, n_bundles: int):
        assert n_bundles == self._n_bundles
        out = np.zeros((self.BUNDLE_HEIGHT * n_bundles, 2048), dtype=np.uint16)
        time.sleep(1)
        return (out, out.copy())
