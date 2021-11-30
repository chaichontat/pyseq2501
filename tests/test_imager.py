#%%
import sys
import time
from pathlib import Path

sys.path.append((Path(__file__).parent.parent).as_posix())
from src.utils.ports import get_ports

ports = get_ports(timeout=60)

from rich import print
from rich.logging import RichHandler

print("[green]Holding breath...")

import logging

logging.basicConfig(
    level="NOTSET",
    format="[yellow]%(name)-10s[/] %(message)s",
    datefmt="[%X]",
    handlers=[RichHandler(rich_tracebacks=True, markup=True)],
)

logging.getLogger("DCAMAPI").setLevel(logging.INFO)


from src.imaging.imager import Imager

god = Imager(ports)
god.fpga.initialize()
god.y.move(132000)
time.sleep(8)
#%%
god.take_image(8)
print("Init")
time.sleep(2)
