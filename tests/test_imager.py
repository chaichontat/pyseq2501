#%%
import sys
from pathlib import Path

sys.path.append("c:\\Users\\sbsuser\\Desktop\\goff-rotation")
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
print("Init")
# god.y.move(0)
#%%
a = god.take_image(5)
# god.initialize()
# %%
