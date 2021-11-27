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

from src.imaging.camera.dcam import Cameras

print("[green]Holding breath...")
#%%
test = Cameras()


#%%
import time
from ctypes import POINTER, c_double, c_int32, c_uint16, c_uint32, c_void_p, pointer

from src.imaging.camera import API

DCAMWAIT_CAPEVENT_FRAMEREADY = 0x0002

test.properties["trigger_source"] = 1
test.properties["sensor_mode"] = 1
API.dcam_precapture(test[0].handle, DCAM_CAPTURE_MODE.SEQUENCE)
API.dcam_precapture(test[1].handle, DCAM_CAPTURE_MODE.SEQUENCE)
exp = 0.3
test.properties["exposure_time"] = exp


# %%
n_bundles = 5
taken = 0
t = test.capture(5)
# with test[0].alloc(n_bundles) as buf:
#     with test[0].capture():
#         while (curr := test[0].n_frames_taken) < n_bundles:
#             for i in range(taken, curr):
#                 test[0].test_get(buf, i)

#%%


# get_mode_key(test.handle, test)
# import pickle

# print(test.properties)
# Path("what.pk").write_bytes(pickle.dumps(test.properties._dict))
#%%
# import sys
# from pathlib import Path

# # from src.instruments.camera.dcam_mode_key import get_mode_key

# sys.path.append("c:\\Users\\sbsuser\\Desktop\\goff-rotation")
# import pickle
# from pathlib import Path

# d = pickle.loads(Path("what.pk").read_bytes())

# %%
