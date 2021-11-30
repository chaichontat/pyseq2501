import sys
import time
from pathlib import Path

sys.path.append((Path(__file__).parent.parent).as_posix())
import logging

from rich import print
from rich.logging import RichHandler
from src.eventloop import LOOP
from src.imaging.laser import Laser
from src.utils.async_com import COM, CmdParse
from src.utils.ports import get_ports

logging.basicConfig(
    level="NOTSET",
    format="[yellow]%(name)-10s[/] %(message)s",
    datefmt="[%X]",
    handlers=[RichHandler(rich_tracebacks=True, markup=True)],
)

logger = logging.getLogger("rich")
logging.getLogger("DCAMAPI").setLevel(logging.INFO)

ports = get_ports(timeout=5, show_all=True)


#%%
from src.imaging.xstage import XStage

# x = XStage(ports.x)
# x.initialize()
x = COM(name="x", port_tx=ports.x)
x.send("PR MV")
x.send("PR P")

# %%
fpga = COM("fpga", *ports.fpga)
fpga.send("RESET")

#%%
las = Laser("laser_r", ports.laser_r)

#%%
time.sleep(10)
