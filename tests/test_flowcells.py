import asyncio
from unittest.mock import patch

import pytest
import pytest_asyncio

from pyseq2.flowcell import FlowCells
from pyseq2.utils.ports import get_ports


@pytest_asyncio.fixture(scope="module")
async def fcs() -> FlowCells:
    ports = await get_ports()
    return await FlowCells.ainit(ports)


async def test_initialize(fcs: FlowCells):
    await fcs.initialize()


async def test_pump(fcs: FlowCells):
    await fcs.A.flow(1, wait=0.1)


async def test_valves(fcs: FlowCells):
    await fcs.A.v.pos

    async with fcs.A.v.move_port(10):
        ...

    await asyncio.gather(*[fcs.A.v._move(p) for p in (0, 1, 10)])

    with pytest.raises(ValueError):
        await fcs.A.v._move(24)

    with pytest.raises(NotImplementedError):
        await fcs.A.v.set_fc_inlet(8)


async def test_valves_2500(fcs: FlowCells):
    with (
        patch("pyseq2.config.CONFIG.Config.allow_mutation", True),
        patch("pyseq2.config.CONFIG.machine", "HiSeq2500"),
    ):
        await fcs.A.v.pos
        await fcs.A.v.set_fc_inlet(8)
        await asyncio.gather(*[fcs.A.v._move(p) for p in (0, 1, 10, 24)])


async def test_arm9chem(fcs: FlowCells):
    await fcs.arm9chem.fc_temp(0)
    await fcs.arm9chem.chiller_temp(0)
    await fcs.arm9chem.set_fc_temp(0, 25)
    await fcs.arm9chem.set_chiller_temp(0, 5)
    await fcs.arm9chem.set_vacuum(False)
