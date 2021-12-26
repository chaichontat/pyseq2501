#%%
import logging
import time

from PIL import Image
from pyseq2.imager import Imager
from pyseq2.utils.ports import get_ports
from rich.logging import RichHandler

logging.basicConfig(
    level="INFO",
    format="[yellow]%(name)-20s[/] %(message)s",
    datefmt="[%X]",
    handlers=[RichHandler(rich_tracebacks=True, markup=True)],
)

ports = get_ports(timeout=60)
imager = Imager(ports, init_cam=True)

#%%
imager.y.move(1000000)
img = imager.take(16, dark=True)
Image.fromarray(img[2]).save("dark.tiff")
time.sleep(0.5)

# %%
