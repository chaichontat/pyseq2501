import pytest

from pyseq2.imager import Imager


@pytest.fixture(autouse=True)
def reset_singleton():
    Imager.instance = None
