import base64
from io import BytesIO

import matplotlib.pyplot as plt
import numpy as np
from PIL import Image
from pydantic import BaseModel


class Hist(BaseModel):
    counts: list[int]
    bin_edges: list[float]


class Img(BaseModel):
    n: int
    img: list[str]
    hist: list[Hist]
    channels: tuple[bool, bool, bool, bool]


def update_img(arr: np.ndarray):
    img = [process_img(i) for i in arr]
    hist = [gen_hist(i) for i in arr]
    return Img(n=arr.shape[1] // 128, img=img, hist=hist, channels=(True, True, True, True))


def process_img(img: np.ndarray) -> str:
    cmap = plt.cm.get_cmap()
    norm = plt.Normalize(vmin=img.min(), vmax=img.max())
    img = (cmap(norm(img)) * 256).astype(np.uint8)

    buff = BytesIO()
    pil_img = Image.fromarray(img).convert("RGB")
    pil_img.save(buff, format="JPEG")
    return "data:image/jpg;base64," + base64.b64encode(buff.getvalue()).decode("utf-8")


def gen_hist(img: np.ndarray) -> Hist:
    hist, bin_edges = np.histogram(img.flatten(), 40)
    return Hist(counts=list(hist), bin_edges=list(bin_edges))
