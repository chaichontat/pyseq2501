import asyncio

from pyseq2.utils.ports import get_ports

asyncio.run(get_ports(show_all=True))
