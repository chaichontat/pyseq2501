from concurrent.futures import Future, ThreadPoolExecutor
from functools import wraps
from logging import getLogger
import threading
from typing import Callable, ParamSpec, TypeVar
import warnings

P, T = ParamSpec("P"), TypeVar("T")


def run_in_executor(f: Callable[P, T]) -> Callable[P, Future[T]]:
    """Attempts to run a function in an executor.
    If the caller is a thread in the object's executor,
    simply wrap with Future and return.

    Any exceptions raised would be shown in warnings and in the log.

    Args:
        f (Callable[P, T]): Instance method. Expects self as the first argument.
            Class must have a ThreadPoolExecutor as self._executor or self.com._executor.

    Raises:
        e: AttributeError when there's no executor.

    Returns:
        Callable[P, Future[T]]: Wrapped function that does not block
            (if you are not calling from within the executor).
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
                    warnings.warn(f"Uncaught exception {type(e).__name__} in thread.")
                    getLogger(type(self).__name__).error(f"Uncaught exception {type(e).__name__} in thread.")
                    raise e

            return exc.submit(g)
        else:
            future: Future[T] = Future()
            future.set_result(f(*args, **kwargs))
            return future

    return inner


def warn_main_thread(f: Callable[P, T]) -> Callable[P, T]:
    """Wraps function to warn that a function that is meant to be run in
    an executor is running on the main thread, potentially blocking it.

    Args:
        f (Callable[P, T])

    Returns:
        Callable[P, T]: Same as input.
    """

    @wraps(f)
    def inner(*args: P.args, **kwargs: P.kwargs) -> T:
        if threading.current_thread() is threading.main_thread():
            warnings.warn(f"{f.__name__} is running on main thread.")
        return f(*args, **kwargs)

    return inner
