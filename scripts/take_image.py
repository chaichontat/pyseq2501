#%%
import logging
import time

import matplotlib.pyplot as plt
from PIL import Image
from pyseq2.imager import Imager
from pyseq2.utils.ports import get_ports
from rich.logging import RichHandler
from rich.traceback import install

install()
logging.basicConfig(
    level="DEBUG",
    format="[yellow]%(name)-20s[/] %(message)s",
    datefmt="[%X]",
    handlers=[RichHandler(rich_tracebacks=True, markup=True)],
)
logging.getLogger("matplotlib.font_manager").setLevel(logging.WARNING)

ports = get_ports(timeout=60)
imager = Imager(ports, init_cam=True)

#%%
imager.y.move(1000000)
img = imager.take(12, dark=True, cam=0)
Image.fromarray(img[0]).save("dark.tiff")
time.sleep(0.5)

# %%

target, focus_plot = imager.autofocus(channel=0)
plt.plot(focus_plot)
# %%
