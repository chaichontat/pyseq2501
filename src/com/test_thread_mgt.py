import time
from concurrent.futures import ThreadPoolExecutor

import pytest

from .thread_mgt import run_in_executor, warn_main_thread


class Fake:
    def __init__(self) -> None:
        self._executor = ThreadPoolExecutor(max_workers=1)

    @run_in_executor
    @warn_main_thread
    def another_thread(self, a: int) -> int:
        time.sleep(0.01)
        if a == 0:
            return 0
        return self.another_thread(a - 1).result()

    @run_in_executor
    @warn_main_thread
    def should_not_warn(self, a: int) -> int:
        return a + 1

    @warn_main_thread
    def should_warn(self, a: int) -> int:
        return a + 1


def test_warning():
    with pytest.warns(UserWarning):
        Fake().should_warn(5)
    Fake().should_not_warn(5)


def test_run_in_executor():
    """Test for piled up `run_in_executor` code."""
    assert Fake().another_thread(3).result() == 0
