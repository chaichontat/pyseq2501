# Run this in Jupyter or Shift+Enter in VSCode.
# https://ipython.readthedocs.io/en/stable/interactive/autoawait.html

from pyseq2.imager import Imager
from pyseq2.utils.log import setup_logger
from pyseq2.utils.ports import get_ports


async def test_take():
    setup_logger()
    ports = await get_ports()
    imager = await Imager.ainit(ports)
    # await imager.initialize()  # If not initialized in this session (defined by HiSeq power cycle).

    # target, focus_plot = await imager.autofocus(channel=0)
    # plt.plot(focus_plot)
    await imager.y.move(1000000)
    img, state = await imager.take(20, dark=True, channels=frozenset((0, 1, 2, 3)))
    await imager.save("test.tiff", img)
