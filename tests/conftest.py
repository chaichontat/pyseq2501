import asyncio

import pytest

from pyseq2.imager import Imager


@pytest.fixture(scope="session")
def event_loop():
    """Create an instance of the default event loop for each test case.
    https://github.com/pytest-dev/pytest-asyncio/issues/171#issuecomment-650780032
    """
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.fixture(autouse=True)
def reset_singleton():
    Imager.instance = None
