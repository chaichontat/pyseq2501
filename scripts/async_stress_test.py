import asyncio
import logging

from rich.logging import RichHandler

from pyseq2.fluidics.arm9chem import ARM9Chem
from pyseq2.fluidics.pump import Pump
from pyseq2.fluidics.valve import Valves
from pyseq2.imaging.fpga import FPGA
from pyseq2.imaging.xstage import XStage
from pyseq2.imaging.ystage import YStage
from pyseq2.utils.ports import get_ports

logging.basicConfig(
    level="NOTSET",
    format="[yellow]%(name)-10s[/] %(message)s",
    datefmt="[%X]",
    handlers=[RichHandler(rich_tracebacks=True, markup=True)],
)


async def temp() -> None:
    temp = await ARM9Chem.ainit((await get_ports())["arm9chem"])
    await temp.initialize()


async def x() -> None:
    x = await XStage.ainit((await get_ports())["x"])
    await x.move(30000)
    await x.pos
    asyncio.create_task(x.move(50000))
    await asyncio.sleep(0.05)
    await x.pos
    await asyncio.sleep(0.5)
    await x.pos
    await asyncio.sleep(0.5)
    await x.pos
    await asyncio.sleep(0.5)
    # Pos should return immediately but
    # move should wait until previous move is done.
    await asyncio.gather(x.move(40000), x.pos)
    await asyncio.sleep(0.3)
    await x.pos


async def y() -> None:
    y = await YStage.ainit((await get_ports())["y"])
    await y.move(1_000_000)
    await y.pos
    asyncio.create_task(y.move(0))
    await asyncio.sleep(0.05)
    await y.pos
    await asyncio.sleep(0.5)
    await y.pos
    await asyncio.sleep(0.5)
    await y.pos
    await asyncio.sleep(0.5)
    # Pos should return immediately but
    # move should wait until previous move is done.
    await asyncio.gather(y.move(1_000_000), y.pos)
    await asyncio.sleep(0.3)
    await y.pos


async def fpga() -> None:
    ports = await get_ports()
    fpga = await FPGA.ainit(ports["fpgacmd"], ports["fpgaresp"])

    zt = fpga.z_tilt
    zo = fpga.z_obj
    opt = fpga.optics
    await zt.pos
    await zt.move(15000)
    await zt.pos

    await fpga.initialize_all()
    # FPGA commands do not support querying for pos while moving.
    # So these will run sequentially in random order.
    await asyncio.gather(zt.move(17000), zt.pos)
    await asyncio.gather(zt.move(18000), zo.move(30000), opt._close())
    await zt.pos
    await asyncio.sleep(0.5)
    await zt.pos
    await asyncio.sleep(0.5)

    await zo.pos
    await zo.move(30000)
    await zo.pos
    await asyncio.gather(zo.move(40000), zo.move(50000), zo.pos)


async def valves():
    ports = await get_ports()
    p = await Valves.ainit("A", ports["valve_a1"], ports["valve_a2"])
    await p.initialize()
    await p.pos
    await asyncio.gather(p._move(3), p._move(4), p.pos)
    await asyncio.gather(p._move(3), p._move(3), p.pos)


async def pump():
    p = await Pump.ainit("pumpa", (await get_ports())["pumpa"])
    await p.initialize()
    await p.pump(48000)


if __name__ == "__main__":
    asyncio.run(valves())
