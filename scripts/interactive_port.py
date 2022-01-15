import asyncio
import logging

from pyseq2.base.instruments_types import SerialInstruments
from pyseq2.com.async_com import COM


async def interactive() -> None:
    import aioconsole
    from pyseq2.utils.ports import get_ports
    from rich.logging import RichHandler

    logging.basicConfig(
        level="NOTSET",
        format="[yellow]%(name)-10s[/] %(message)s",
        datefmt="[%X]",
        handlers=[RichHandler(rich_tracebacks=True, markup=True)],
    )

    name: SerialInstruments = await aioconsole.ainput("Instrument? ")
    com = await COM.ainit(name, getattr(await get_ports(), name))
    while True:
        await asyncio.sleep(0.2)
        line = await aioconsole.ainput("Command? ")
        if line == "exit":
            return
        await aioconsole.aprint()
        await com.send(line)


if __name__ == "__main__":
    asyncio.run(interactive())
