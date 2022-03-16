import asyncio

import pytest_asyncio

from pyseq2.experiment import Experiment
from pyseq2.experiment.command import Autofocus, Goto, Hold, Prime, Pump, TakeImage, Temp
from pyseq2.experiment.reagent import Reagent
from pyseq2.flowcell import FlowCells
from pyseq2.imager import Imager
from pyseq2.utils.ports import get_ports


@pytest_asyncio.fixture(scope="module")
async def fcs() -> FlowCells:
    ports = await get_ports(show_all=True)
    return await FlowCells.ainit(ports)


@pytest_asyncio.fixture(scope="module")
async def imager() -> Imager:
    ports = await get_ports()
    return await Imager.ainit(ports)


async def test_run(imager: Imager, fcs: FlowCells):
    exp = Experiment(
        name="test",
        fc=False,
        path=".",
        reagents=[Reagent(name="water", port=14, wait=0.1)],
        cmds=[Pump(reagent="water") for _ in range(10)],
    )
    await exp.run(fcs, False, imager)


async def test_commands(imager: Imager, fcs: FlowCells):
    q: asyncio.Queue[tuple[int, int, int]] = asyncio.Queue()
    reagent = Reagent(name="water", port=14, wait=0.1)
    args = (fcs, False, imager)
    await Pump(reagent=reagent).run(*args)
    await Prime(reagent=reagent).run(*args)
    await Temp(temp=0).run(*args)
    await Hold(time=0.1).run(*args)
    await Autofocus.default().run(*args)
    t = TakeImage.default()
    t.save = True
    await t.run(*args, q)
    assert q.qsize() > 0
    Goto.default()
