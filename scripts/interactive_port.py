import logging

from pyseq2.com.async_com import COM
from pyseq2.utils.ports import get_ports
from rich.logging import RichHandler

logging.basicConfig(
    level="NOTSET",
    format="[yellow]%(name)-10s[/] %(message)s",
    datefmt="[%X]",
    handlers=[RichHandler(rich_tracebacks=True, markup=True)],
)

ports = get_ports(timeout=60)
com = COM("y", ports.y, no_check=True)
while True:
    com.send(input())
