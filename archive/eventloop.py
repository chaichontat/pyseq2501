import asyncio
from asyncio.events import AbstractEventLoop
from concurrent.futures import Future
from functools import wraps
from threading import Thread
from typing import Any, Awaitable, Callable, Optional, ParamSpec, TypeVar

# Derived from https://www.linw1995.com/en/blog/Run-Asyncio-Event-Loop-in-another-thread/
# Ron Frederick has thought of a smart way to kill the event loop and the thread using callback from another thread.
# https://github.com/ronf/asyncssh/issues/295#issuecomment-659143796
# Without this, the thread running the event loop will run forever, and the program could not exit normally.
# loop.call_soon_threadsafe(loop.stop)

"""Generates a global variable LOOP that holds the event loop thread.
"""

T = TypeVar("T")


class AsyncioEventLoopThread(Thread):
    """Basically an event loop running in a thread."""

    def __init__(self, loop: Optional[AbstractEventLoop] = None):
        def endless_event_loop(loop: AbstractEventLoop) -> None:
            asyncio.set_event_loop(loop)
            loop.run_forever()

        self.loop = loop if loop is not None else asyncio.new_event_loop()
        super().__init__(target=endless_event_loop, args=(self.loop,), daemon=True)
        self.start()

    def put(self, coro: Awaitable[T]) -> Future[T]:
        return asyncio.run_coroutine_threadsafe(coro, loop=self.loop)

    def join(self, timeout: Optional[float] = None) -> None:
        self.loop.call_soon_threadsafe(self.loop.stop)
        super().join(timeout)

    def stop(self):
        self.loop.call_soon_threadsafe(self.loop.stop)
        self.join()


def init_loop() -> None:
    global LOOP
    LOOP = AsyncioEventLoopThread()


try:
    LOOP  # type: ignore
except NameError:
    init_loop()

P = ParamSpec("P")


def run_in_loop(f: Callable[P, Awaitable[T]]) -> Callable[P, Future[T]]:
    LOOP: AsyncioEventLoopThread

    @wraps(f)
    def wrapper(*args: Any, **kwargs: Any) -> Future[T]:
        return LOOP.put(f(*args, **kwargs))

    return wrapper
