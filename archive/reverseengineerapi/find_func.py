#%%
# from . import API
import re
from pathlib import Path

api = Path("dcamapi3.h").read_text()
prop = Path("dcamprop.h").read_text()
miss = Path("missing.h.cpp").read_text()
# md = Path("dcam.md").read_text()
s = Path("test.pyi").read_text()
# %%
cand = set(re.findall(r"^BOOL DCAMAPI (dcam_\w+)", api, re.M))
cand |= set(re.findall(r"^BOOL DCAMAPI (dcam_\w+)", prop, re.M))
miss = set(re.findall(r"^BOOL DCAMAPI (dcam_\w+)", miss, re.M))
x = re.findall(r"^    def (\w+)", s, re.M)
# %%
from ctypes import Structure, WinDLL, pointer, c_double, c_int32, c_void_p, sizeof  # type: ignore

w = WinDLL("dcamapi.dll")
succ = set()
for f in miss:
    try:
        getattr(w, f)
        succ.add(f)
    except AttributeError:
        print(f)

# %%


# %%
sp = iter(md.split("\n\n"))
out = []
for x in sp:
    out.append((x.lower(), next(sp)))


# %%
processed = []
s = Path("test.pyi").read_text()
lines = s.split("\n")
for i in range(len(lines)):
    if not (lines[i].startswith("    def") and lines[i].endswith("...")):
        continue
    if (f_name := re.match(r"^    def (\w+)\(", lines[i])) is None:
        continue

    f_name = f_name.group(1)
    try:
        _, desp = list(filter(lambda x: x[0] == f_name, out))[0]
    except IndexError:
        print(f_name)
    else:
        lines[i] = lines[i][:-3] + '"""' + desp + '"""'

# %%
Path("test2.pyi").write_text("\n".join(lines))
# %%
