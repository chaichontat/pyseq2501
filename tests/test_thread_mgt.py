import time
from concurrent.futures import ThreadPoolExecutor

import pytest
from pyseq2.com.thread_mgt import run_in_executor, warn_main_thread


class Fake:
    def __init__(self) -> None:
        self._executor = ThreadPoolExecutor(max_workers=1)

    @run_in_executor
    @warn_main_thread
    def another_thread(self, a: int) -> int:
        time.sleep(0.01)
        if a == 0:
            return 0
        return self.another_thread(a - 1).result(1)

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


class Raiser:
    @run_in_executor
    def no_executor(self):
        return 1

    @run_in_executor
    def raiseexc(self):
        raise NotImplementedError


def test_exception():
    """Test Exception handling in run_in_executor."""
    t = ThreadPoolExecutor(max_workers=1)
    r = Raiser()
    with pytest.raises(AttributeError):
        r.no_executor()

    r._executor = t  # type: ignore
    with pytest.warns(UserWarning):
        r.raiseexc()
