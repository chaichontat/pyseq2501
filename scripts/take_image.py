#%%
# Run this in Jupyter or Shift+Enter in VSCode.
# https://ipython.readthedocs.io/en/stable/interactive/autoawait.html

import asyncio

import matplotlib.pyplot as plt
from PIL import Image

from pyseq2.imager import Imager
from pyseq2.utils.log import setup_logger
from pyseq2.utils.ports import get_ports

setup_logger(to_file=False)
q: asyncio.Queue[int] = asyncio.Queue()


async def watch():
    while True:
        print(await q.get())


ports = await get_ports()
imager = await Imager.ainit(ports)
# await imager.initialize()  # If not initialized in this session (defined by HiSeq power cycle).

# target, focus_plot = await imager.autofocus(channel=0)
# plt.plot(focus_plot)
# If init takes too long, repeat.
await imager.y.move(1000000)

asyncio.create_task(watch())
img = await imager.take(20, dark=True, channels=frozenset((0, 1)), event_queue=q)
Image.fromarray(img[0]).save("dark.tiff")
print("Done!")

# %%
