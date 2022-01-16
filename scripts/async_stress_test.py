import asyncio
import logging

from pyseq2.fluidics.temperature import Temperature
from pyseq2.imaging.fpga import FPGA
from pyseq2.imaging.xstage import XStage
from pyseq2.imaging.ystage import YStage
from pyseq2.utils.ports import get_ports
from rich.logging import RichHandler

logging.basicConfig(
    level="NOTSET",
    format="[yellow]%(name)-10s[/] %(message)s",
    datefmt="[%X]",
    handlers=[RichHandler(rich_tracebacks=True, markup=True)],
)


async def temp() -> None:
    temp = await Temperature.ainit((await get_ports())["arm9chem"])
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
    await zt.pos
    await zt.move(15000)
    await zt.pos
    # FPGA commands do not support querying for pos while moving.
    # So these will run sequentially in random order.
    await asyncio.gather(zt.move(17000), zt.pos)
    asyncio.create_task(zt.move(18000))
    await zt.pos
    await asyncio.sleep(0.5)
    await zt.pos
    await asyncio.sleep(0.5)

    zo = fpga.z_obj
    await zo.pos
    await zo.move(30000)
    await zo.pos
    await asyncio.gather(zo.move(40000), zo.move(50000), zo.pos)


if __name__ == "__main__":
    asyncio.run(x())
    asyncio.run(y())
    asyncio.run(fpga())
