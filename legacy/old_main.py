import logging

from pyseq import HiSeq
from rich.logging import RichHandler

logging.basicConfig(
    level="NOTSET", format="%(message)s", datefmt="[%X]", handlers=[RichHandler(rich_tracebacks=True)]
)

log = logging.getLogger("rich")

hs = HiSeq(Logger=log)
hs.initializeCams(Logger=log)
# hs.initializeInstruments()

hs.image_path = "C:\\Users\\sbsuser\\Desktop\\goff-rotation\\images\\"
x_begin = 20
y_begin = 15
size = 1
pos = hs.position("A", [x_begin, y_begin, x_begin - size, y_begin - size])
# hs.y.move(pos["y_initial"])
#%%
hs.x.move(pos["x_initial"])
hs.z.move([20000, 20000, 20000])
hs.obj.move(30000)
hs.optics.move_ex("green", "open")
hs.optics.move_ex("red", "open")
hs.optics.move_em_in(True)
#%%
hs.y.move(pos["y_initial"])
#%%
hs.take_picture(64, "128")
# # %%
