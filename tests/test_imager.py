#%%
import logging
import sys
import time
from pathlib import Path

from PIL import Image
from rich.logging import RichHandler

sys.path.append((Path(__file__).parent.parent).as_posix())


from src.imager import Imager
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
imager.fpga.reset().result()

#%%
imager.y.move(1000000)

# fut = (imager.lasers.g.set_power(30), imager.lasers.r.set_power(30))
# wait(fut)

img = imager.take(16, dark=True)
Image.fromarray(img[2]).save("dark.tiff")
time.sleep(0.5)
