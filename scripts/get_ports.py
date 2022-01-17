import asyncio

from pyseq2.utils.ports import get_ports


async def ports():
    p = await get_ports(show_all=True)
    print(p)

asyncio.run(ports())
