#%%
import sys
from pathlib import Path

sys.path.append("c:\\Users\\sbsuser\\Desktop\\goff-rotation")
import logging

from rich import print
from rich.console import Console
from rich.logging import RichHandler
from src.imaging.camera.dcam_api import DCAM_CAPTURE_MODE

logging.basicConfig(
    level="NOTSET",
    format="[yellow]%(name)-10s[/] %(message)s",
    datefmt="[%X]",
    handlers=[RichHandler(rich_tracebacks=True, markup=True)],
)

log = logging.getLogger("rich")
logging.getLogger("DCAMAPI").setLevel(logging.INFO)

from src.imaging.camera.dcam import Cameras, Mode

print("[green]Holding breath...")
#%%
cams = Cameras()


#%%
import time
from ctypes import POINTER, c_double, c_int32, c_uint16, c_uint32, c_void_p, pointer

from src.imaging.camera import API

# DCAMWAIT_CAPEVENT_FRAMEREADY = 0x0002

# test.properties["trigger_source"] = 1
# test.properties["sensor_mode"] = 1
API.dcam_precapture(cams[0].handle, DCAM_CAPTURE_MODE.SNAP)
API.dcam_precapture(cams[1].handle, DCAM_CAPTURE_MODE.SNAP)

# exp = 0.3
# test.properties["exposure_time"] = exp
# cams.mode = Mode.AUTOFOCUS
n_bundles = 10
with cams._alloc(n_bundles) as bufs:
    taken = 0
    with cams[0].capture(), cams[1].capture():
        t0 = time.time()
        while (avail := cams.n_frames_taken) < n_bundles:
            time.sleep(0.1)
            if avail > taken:
                print(f"Now at {avail}")
                taken = avail


# %%
taken = 0


#%%
from ctypes import POINTER, c_double, c_int32, c_uint16, c_uint32, c_void_p, pointer

import numpy as np

n = 32
arr = np.ones((n * 128, 4096), dtype=np.uint16)
addr = arr.ctypes.data

# pointer((c_uint16 * (n * 128) * 4096)())

t = (c_void_p * n)()
for i in range(n):
    t[i] = 524288 * i + addr

# %%
# cams[0].properties._dict["trigger_source"].mode_key(cams[0].handle)
{"sensor_mode": 6, "exposure_time": 0.0022, "partial_area_vsize": 5}
