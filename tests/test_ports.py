#%%
import sys
from pathlib import Path

sys.path.append("c:\\Users\\sbsuser\\Desktop\\goff-rotation")
from src.imaging.fpga import FPGA
from src.imaging.laser import Laser
from src.imaging.xstage import XStage
from src.utils.ports import get_ports

ports = get_ports(timeout=60, show_all=True)

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


# %%
logger = logging.getLogger()
from src.utils.com import COM

fpga = FPGA(*ports.fpga)
# fpga.initialize()

# %%

laser = Laser(ports.laser_g)
laser.set_onoff(True)
laser.set_power(30)
# %%
from src.imaging.ystage import YStage

y = YStage(ports.y)
# %%
from src.imaging.xstage import XStage

x = XStage(ports.x)


#%%
x.com.repl("EM=2")
#%%
y.initialize()
x.initialize()
# %%
from src.utils.utils import position

x_begin = 20
y_begin = 15
size = 1
pos = position("B", [x_begin, y_begin, x_begin - size, y_begin - size])

x.com.repl(x.cmd.SET_POS(pos["x_initial"]))
# %%
y.com.repl([y.cmd.SET_POS(1320000), y.cmd.GO, y.cmd.READ_POS])
#%%

# TODO: Check which command actually responds
# HM -> multiple lines
# CR Repeat oneline
# MOVETO oneline ==== T1MOVETO {n}

fpga.com.repl([f"T{i}HM" for i in range(1, 4)])
# fpga.com.repl([f"T{i}MOVETO 21500" for i in range(1, 4)])

# %%
from src.imaging.fpga.zstage import ZStage

z = ZStage(fpga.com)
z.move(1000)
# %%
import numpy as np

x = np.loadtxt("../purim.txt")
#%%
import matplotlib.pyplot as plt
from PIL import Image

im = Image.fromarray(A)
im.save("your_file.jpeg")
