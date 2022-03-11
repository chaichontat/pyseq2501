import argparse
import asyncio
import logging

from pyseq2.flowcell import FlowCells
from pyseq2.imager import Imager
from pyseq2.utils.ports import get_ports

logging.basicConfig(level=logging.DEBUG)


async def init():
    p = await get_ports()
    imager = await Imager.ainit(p)
    fcs = await FlowCells.ainit(p)
    await asyncio.gather(imager.initialize(), fcs.initialize())


async def pump():
    p = await get_ports()
    fcs = await FlowCells.ainit(p)
    await fcs.initialize()
    await fcs[0].flow(1)


async def eject():
    p = await get_ports()
    imager = await Imager.ainit(p, init_cam=False)
    await imager.move(x=20000, y=int(-6e6))


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("command", type=str, help="Commands: init, pump, eject")
    args = parser.parse_args()
    asyncio.run(globals()[args.command]())
