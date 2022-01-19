import asyncio
import logging

from pyseq2.flowcell import FlowCells
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
    fcs = await FlowCells.ainit(ports)
    await fcs.initialize()
    await asyncio.gather(fcs[0].wash(10), fcs[1].wash(10))


if __name__ == "__main__":
    asyncio.run(main())
