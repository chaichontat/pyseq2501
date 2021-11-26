#%%
DUMMY = False

from rich import print
from rich.console import Console
from rich.logging import RichHandler

from friendly_hiseq import Components

print("[green]Holding breath...")

if not DUMMY:
    from friendly_hiseq import FriendlyHiSeq
else:
    from dummy import FriendlyHiSeq  # type: ignore

import logging

logging.basicConfig(
    level="NOTSET", format="%(message)s", datefmt="[%X]", handlers=[RichHandler(rich_tracebacks=True)]
)

logger = logging.getLogger("rich")
console = Console()

hs = FriendlyHiSeq(console=console)
#%%
# init_ui(hs.gen_initialize_seq(skip=[Components.PUMPS, Components.VALVES]))
#%%
hs.image_path = "C:\\Users\\sbsuser\\Desktop\\goff-rotation\\images\\"
hs.initializeCams()

#%%
x_begin = 15
y_begin = 15
size = 1
pos = hs.position("B", [x_begin, y_begin, x_begin - size, y_begin - size])
# hs.y.move(pos["y_initial"])
#%%
hs.x.move(pos["x_initial"])
hs.z.move([20000, 20000, 20000])
hs.obj.move(30000)
hs.optics.move_ex("green", "open")
hs.optics.move_ex("red", "open")
hs.optics.move_em_in(True)
#%%
hs.lasers["green"].set_power(30)
#%%
hs.y.move(pos["y_initial"] + 2100000)
#%%
hs.take_picture(16, "128aligned")

# # %%

#%%
for z in [21600, 21800]:
    hs.z.move([z, z, z])
    hs.y.move(pos["y_initial"] + 2200000)
    hs.take_picture(16, f"128al{z}")
#%%
# %%
