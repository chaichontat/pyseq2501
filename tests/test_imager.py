#%%
import logging
import time

from PIL import Image
from pyseq2.imager import Imager
from pyseq2.utils.ports import get_ports
from rich.logging import RichHandler

logging.basicConfig(
    level="NOTSET",
    format="[yellow]%(name)-10s[/] %(message)s",
    datefmt="[%X]",
    handlers=[RichHandler(rich_tracebacks=True, markup=True)],
)

logging.getLogger("DCAMAPI").setLevel(logging.INFO)

ports = get_ports(timeout=60)
imager = Imager(ports, init_cam=True)

#%%
imager.y.move(1000000)

# fut = (imager.lasers.g.set_power(30), imager.lasers.r.set_power(30))
# wait(fut)

img = imager.take(16)
Image.fromarray(img[2]).save("dark.tiff")
time.sleep(0.5)

# %%
