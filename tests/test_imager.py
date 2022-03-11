from contextlib import nullcontext

import pytest
import pytest_asyncio

from pyseq2.imager import Imager
from pyseq2.utils.ports import get_ports


@pytest_asyncio.fixture(scope="module")
async def imager() -> Imager:
    ports = await get_ports()
    imager = await Imager.ainit(ports)
    return imager


async def test_initialize(imager: Imager):
    await imager.initialize()


@pytest.mark.parametrize("c", range(16))
async def test_take(imager: Imager, c: int):
    channels = [i for i, x in enumerate([c & 1, c & 2, c & 4, c & 8]) if x]
    with pytest.raises(ValueError) if not len(channels) else nullcontext():
        img, _ = await imager.take(1, channels=channels)
        assert img.shape[0] == len(channels)
