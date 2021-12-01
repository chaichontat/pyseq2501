#%%
import logging
import sys
import time
from pathlib import Path

from rich.logging import RichHandler

sys.path.append((Path(__file__).parent.parent).as_posix())


from src.imaging.imager import Imager
from src.utils.ports import get_ports

logging.basicConfig(
    level="NOTSET",
    format="[yellow]%(name)-10s[/] %(message)s",
    datefmt="[%X]",
    handlers=[RichHandler(rich_tracebacks=True, markup=True)],
)

logging.getLogger("DCAMAPI").setLevel(logging.INFO)
ports = get_ports(timeout=60)


imager = Imager(ports)
imager.fpga.initialize()
imager.y.move(132000)
#%%
imager.take_image(8)
time.sleep(2)
