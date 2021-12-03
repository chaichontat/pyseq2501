#%%
#%%
import logging
import sys
import time
from pathlib import Path
import numpy as np
import matplotlib.pyplot as plt
from rich.logging import RichHandler

sys.path.append((Path(__file__).parent.parent).as_posix())


from src.imager import Imager
from src.utils.ports import get_ports

logging.basicConfig(
    level="INFO",
    format="[yellow]%(name)-10s[/] %(message)s",
    datefmt="[%X]",
    handlers=[RichHandler(rich_tracebacks=True, markup=True)],
)

logging.getLogger("DCAMAPI").setLevel(logging.INFO)
logging.getLogger("matplotlib.font_manager").setLevel(logging.INFO)
ports = get_ports(timeout=60)
imager = Imager(ports, init_cam=True)
# imager.fpga.initialize()
# imager.y.move(3_000_000)  # Pos is stage out
out = {}
# "MA 39000"a
#%%
out = {}
for z in [22000]:
    imager.y.move(3_000_000)
    imager.z.move(z)
    time.sleep(1)
    out[z] = imager.take_image(16)


# %%


# %%
imager.y.move(820000)
out = imager.take_image(32)
# [print(k, np.mean(v[1][512:])) for k, v in out.items()]
plt.imshow(out[1][512:])
#%%
[print(np.mean(out[i][512:])) for i in range(4)]
# %%
plt.imshow(out[22000][1][128:])
# %%

# %%
from src.utils.utils import position

x_begin = 11
y_begin = 11
size = 1
pos = position("A", [x_begin, y_begin, x_begin - size, y_begin - size])
# %%
imager.cams.properties["sensor_mode"] = 4
zout = {}
for z in [34298, 35298, 36298, 37298]:
    imager.fpga.com.send(f"ZDACW {z}")
    # imager.z.move(z)
    time.sleep(0.5)
    temp = []
    for x in range(-4, 2):
        imager.x.com.send(f"MA {13800 + x * 300}")
        imager.y.move(1770000)
        time.sleep(0.1)
        temp.append(imager.take_image(284))
    zout[z] = temp

# %% Show
for z in zout.keys():
    plt.figure(figsize=(3, 8), dpi=200)
    plt.imshow(stacked := np.hstack([zout[z][i][1][128:, 10:-10] for i in range(len(zout[z]))]))
    plt.title(f"Brightness: {np.mean(stacked)}")
    plt.show()
# %%
imager.z.move(19850)

imager.cams.properties["sensor_mode"] = 6
imager.cams[0].properties.update({"exposure_time": 0.002, "partial_area_vsize": 5})
imager.fpga.com.send("ZSTEP 6442353")
imager.fpga.com.send("ZTRG 0")
imager.fpga.com.send("ZYT 0 3")
imager.fpga.com.send("ZMV 60292")
imager.fpga.com.send("ZDACR")

n_bundles = 232
import time

imager.fpga.com.send("ZSTEP 1288471")
imager.fpga.com.send("SWYZ_POS 1")

with imager.cams._alloc(232, height=5) as bufs:
    with imager.optics.open_shutter():
        imager.fpga.com.send("ZSTEP 541158")
        imager.fpga.com.send("ZTRG 60292")
        print(f"trg{imager.cams[0].n_frames_taken}")
        imager.fpga.com.send("ZYT 0 3")
        print(f"zyt{imager.cams[0].n_frames_taken}")
        with imager.cams[0].capture():
            taken = 0
            imager.fpga.com.send("ZMV 2621")
            while (avail := imager.cams[0].n_frames_taken) < n_bundles:
                time.sleep(0.01)
                if avail > taken:
                    print(avail)
                    # [imager.cams[0].get_bundle(bufs[0], 5, i) for i in range(taken, avail)]
                    # taken = avail

    # Done. Retrieve images.
    for i in range(taken, max(avail, n_bundles)):
        imager.cams[0].get_bundle(buf=bufs[0], height=5, n_curr=i)
# %%
plt.plot(np.mean(bufs[0], axis=1))
target = 450
60292 - (((60292 - 2621) / n_bundles) * (target / 5) + 2621)
# %%
zout[19850][0]

#%%
from PIL import Image

for n in range(len(zout[19850])):
    Image.fromarray(np.array(zout[19850][0])).save(f"35298_{n}.tif")

# %%
import pickle
from pathlib import Path

Path("out.pk").write_bytes(pickle.dumps(zout))
#%%

u = np.stack([np.array(x) for x in zout.values()])

# %%
