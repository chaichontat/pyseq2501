import asyncio
from contextlib import contextmanager
from typing import Coroutine, Generator


@contextmanager
def q_listener(f: Coroutine[None, None, None]) -> Generator[None, None, None]:
    task = asyncio.create_task(f)
    try:
        yield
    finally:
        task.cancel()
