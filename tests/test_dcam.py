#%%
import sys
from pathlib import Path

# from src.instruments.camera.dcam_mode_key import get_mode_key

sys.path.append("c:\\Users\\sbsuser\\Desktop\\goff-rotation")

import logging

from rich import print
from rich.console import Console
from rich.logging import RichHandler

logging.basicConfig(
    level="NOTSET",
    format="[yellow]%(name)-10s[/] %(message)s",
    datefmt="[%X]",
    handlers=[RichHandler(rich_tracebacks=True, markup=True)],
)

log = logging.getLogger("rich")

from src.imaging.camera.dcam import Camera

print("[green]Holding breath...")


test = Camera(0)

# %%
# get_mode_key(test.handle, test)
# import pickle

print(test.properties)
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
