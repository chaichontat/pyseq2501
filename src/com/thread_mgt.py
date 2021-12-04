from concurrent.futures import Future, ThreadPoolExecutor
from functools import wraps
from logging import getLogger
import threading
from typing import Callable, ParamSpec, Protocol, TypeVar, cast
import warnings

P, T = ParamSpec("P"), TypeVar("T")


class Threaded(Protocol):
    _executor: ThreadPoolExecutor


def run_in_executor(f: Callable[P, T]) -> Callable[P, Future[T]]:
    """
    Prevents a race condition in which a result from the running object is dependent on an object in the queue.
    """

    @wraps(f)
    def inner(*args: P.args, **kwargs: P.kwargs) -> Future[T]:
        assert isinstance(args[0], object)
        self = args[0]
        exc: ThreadPoolExecutor
        try:
            exc = self._executor  # type: ignore
        except AttributeError:
            exc = self.com._executor  # type: ignore

        if threading.current_thread() not in exc._threads:

            def g() -> T:
                try:
                    return f(*args, **kwargs)
                except BaseException as e:
                    getLogger(type(self).__name__).critical(f"Uncaught exception {e} in thread.")
                    raise e

            return exc.submit(g)
        else:
            future: Future[T] = Future()
            future.set_result(f(*args, **kwargs))
            return future

    return inner


def warn_main_thread(f: Callable[P, T]) -> Callable[P, T]:
    @wraps(f)
    def inner(*args: P.args, **kwargs: P.kwargs) -> T:
        if threading.current_thread() is threading.main_thread():
            warnings.warn(f"{f.__name__} is running on main thread.")
        return f(*args, **kwargs)

    return inner
