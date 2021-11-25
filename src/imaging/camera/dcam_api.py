#%%
from ctypes import WinDLL


class DCAMAPI(WinDLL):
    def __init__(self) -> None:
        super().__init__("dcamapi.dll")


#%%
