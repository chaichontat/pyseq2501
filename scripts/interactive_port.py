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
    if name.startswith("v"):
        sep = b"\r"
    elif name.startswith("pump"):
        sep = b"\r\n\xff"
    else:
        sep = b"\n"

    ports = await get_ports()
    if name == "fpga":
        com = await COM.ainit(name, ports["fpgacmd"], ports["fpgaresp"], separator=sep)
    else:
        com = await COM.ainit(name, ports[name], separator=sep)

    while True:
        await asyncio.sleep(0.2)
        line = await aioconsole.ainput("Command? ")
        if line == "exit":
            return
        await aioconsole.aprint()
        await com.send(line)


if __name__ == "__main__":
    asyncio.run(interactive())

# %%
