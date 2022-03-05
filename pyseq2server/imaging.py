import base64
from io import BytesIO

import matplotlib.pyplot as plt
import numpy as np
from PIL import Image
from pydantic import BaseModel

from pyseq2.imager import UInt16Array


class Hist(BaseModel):
    counts: list[int]
    bin_edges: list[float]


class AFImg(BaseModel):
    afimg: list[str]


class Img(BaseModel):
    n: int
    img: list[str]
    hist: list[Hist]
    channels: tuple[bool, bool, bool, bool]
    dim: tuple[int, int]


def update_afimg(stack: UInt16Array) -> AFImg:
    minmax = (stack.min(), stack.max())
    return AFImg(afimg=[process_img(i, minmax) for i in stack])


def update_img(arr: UInt16Array) -> Img:
    img = [process_img(i) for i in arr]
    hist = [gen_hist(i) for i in arr]
    return Img(
        n=arr.shape[1] // 128, img=img, hist=hist, channels=(True, True, True, True), dim=arr.shape[1:]
    )


def process_img(img: UInt16Array, minmax: tuple[int, int] | None = None) -> str:
    cmap = plt.cm.get_cmap()
    if minmax is None:
        vmin, vmax = img.min(), img.max()
    else:
        vmin, vmax = minmax
    norm = plt.Normalize(vmin=vmin, vmax=vmax)
    img = (cmap(norm(img)) * 256).astype(np.uint8)  # type: ignore

    buff = BytesIO()
    pil_img = Image.fromarray(img).convert("RGB")
    pil_img.save(buff, format="JPEG")
    return "data:image/jpg;base64," + base64.b64encode(buff.getvalue()).decode("utf-8")


def gen_hist(img: UInt16Array) -> Hist:
    hist, bin_edges = np.histogram(img.flatten(), 40)
    return Hist(counts=list(hist), bin_edges=list(bin_edges))
