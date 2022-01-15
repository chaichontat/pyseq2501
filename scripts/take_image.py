#%%
import asyncio
import logging

import matplotlib.pyplot as plt
from PIL import Image
from pyseq2.imager import Imager
from pyseq2.utils.ports import get_ports
from rich.logging import RichHandler
from rich.traceback import install

install()
logging.basicConfig(
    level="INFO",
    format="[yellow]%(name)-20s[/] %(message)s",
    datefmt="[%X]",
    handlers=[RichHandler(rich_tracebacks=True, markup=True)],
)
logging.getLogger("matplotlib.font_manager").setLevel(logging.WARNING)


async def take():
    ports = await get_ports()
    imager = await Imager.ainit(ports)
    # await imager.initialize()  # If not initialized in this session (defined by HiSeq power cycle).

    target, focus_plot = await imager.autofocus(channel=0)
    plt.plot(focus_plot)

    await imager.y.move(1000000)
    img = await imager.take(12, dark=True, channels=frozenset((0, 1)))
    Image.fromarray(img[0]).save("dark.tiff")


#%%

# %%
if __name__ == "__main__":
    asyncio.run(take())
