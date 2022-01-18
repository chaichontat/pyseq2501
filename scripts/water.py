import asyncio
import logging

from pyseq2.fluidics.arm9chem import ARM9Chem
from pyseq2.fluidics.fluidics import Fluidics
from pyseq2.utils.ports import get_ports
from rich.logging import RichHandler

logging.basicConfig(
    level="NOTSET",
    format="[yellow]%(name)-10s[/] %(message)s",
    datefmt="[%X]",
    handlers=[RichHandler(rich_tracebacks=True, markup=True)],
)


async def main():
    ports = await get_ports()
    arm9chem = await ARM9Chem.ainit(ports["arm9chem"])
    a, b = await asyncio.gather(Fluidics.ainit("A", ports, arm9chem), Fluidics.ainit("B", ports, arm9chem))
    await asyncio.gather(a.initialize(), b.initialize())
    await asyncio.gather(a.maintenance_wash(10), b.maintenance_wash(10))
    # await b.maintenance_wash(7)


if __name__ == "__main__":
    asyncio.run(main())
