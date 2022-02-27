import asyncio
import logging

from pyseq2.base.instruments_types import SerialInstruments
from pyseq2.com.async_com import COM


async def interactive() -> None:
    import aioconsole
    from rich.logging import RichHandler

    from pyseq2.utils.ports import get_ports

    logging.basicConfig(
        level="NOTSET",
        format="[yellow]%(name)-10s[/] %(message)s",
        datefmt="[%X]",
        handlers=[RichHandler(rich_tracebacks=True, markup=True)],
    )

    name: SerialInstruments = await aioconsole.ainput("Instrument? ")

    ports = await get_ports()
    if name == "fpga":
        com = await COM.ainit(name, ports["fpgacmd"], ports["fpgaresp"])
    else:
        com = await COM.ainit(name, ports[name])

    while True:
        await asyncio.sleep(0.2)
        line: str = await aioconsole.ainput("Command? ")
        if line == "exit":
            return
        await aioconsole.aprint()
        await com.send(line)


if __name__ == "__main__":
    asyncio.run(interactive())

# %%
