from __future__ import annotations

from ctypes import Structure, WinDLL, _NamedFuncPointer, c_double, c_int32, c_void_p, sizeof
from enum import IntEnum
from functools import wraps
from typing import Callable, Literal, TypedDict, TypeVar, cast, get_args

FBool = TypeVar("FBool", bound=Callable[..., bool])


class DCAMException(Exception):
    ...


class DCAMReturnedZero(DCAMException):
    ...


def check_if_failed(f: FBool) -> FBool:
    @wraps(f)
    def wrapper(*args, **kwargs) -> bool:
        res = f(*args, **kwargs)
        # Literally the only function that returns int32 instead of BOOL.
        if res == 0 and f.__name__ != "dcam_getlasterror":
            raise DCAMReturnedZero(f"{f.__name__} did not return NOERR.")
        return res

    return cast(FBool, wrapper)


class CheckedDCAMAPI(WinDLL):
    def __init__(self) -> None:
        super().__init__("dcamapi.dll")

    def __getitem__(self, name: str) -> _NamedFuncPointer:
        return check_if_failed(super().__getitem__(name))


Handle = c_void_p

Props = Literal[
    "sensor_mode",
    "sensor_mode_line_bundle_height",
    "colortype",
    "bit_per_channel",
    "trigger_source",
    "trigger_mode",
    "trigger_active",
    "trigger_polarity",
    "trigger_connector",
    "exposure_time",
    "contrast_gain",
    "primary_buffer_mode",
    "binning",
    "subarray_hpos",
    "subarray_hsize",
    "subarray_vpos",
    "subarray_vsize",
    "subarray_mode",
    "number_of_partial_area",
    "partial_area_vpos",
    "partial_area_vsize",
    "timing_readout_time",
    "timing_cyclic_trigger_period",
    "timing_min_trigger_blanking",
    "timing_min_trigger_interval",
    "timing_exposure",
    "internal_frame_rate",
    "internal_frame_interval",
    "internal_line_rate",
    "internal_line_speed",
    "image_width",
    "image_height",
    "image_rowbytes",
    "image_framebytes",
    "image_top_offset_bytes",
    "image_bit_depth_alignment",
    "system_alive",
    "cc2_on_framegrabber",
    "number_of_channel",
    "attach_buffer_target",
    "number_of_target_per_attachbuffer",
]


class PropertyDict(TypedDict):
    sensor_mode: Literal[1, 3, 4, 6]
    sensor_mode_line_bundle_height: int
    colortype: Literal[1]
    bit_per_channel: Literal[12]
    trigger_source: Literal[1, 2]
    trigger_mode: Literal[1]
    trigger_active: Literal[3]
    trigger_polarity: Literal[1, 2]
    trigger_connector: Literal[1, 2]
    exposure_time: float
    contrast_gain: int
    primary_buffer_mode: Literal[1, 2]
    binning: Literal[1, 2]
    subarray_hpos: int
    subarray_hsize: int
    subarray_vpos: int
    subarray_vsize: int
    subarray_mode: Literal[1, 2]
    number_of_partial_area: int
    partial_area_vpos: int
    partial_area_vsize: int
    timing_readout_time: float
    timing_cyclic_trigger_period: float
    timing_min_trigger_blanking: float
    timing_min_trigger_interval: float
    timing_exposure: Literal[1, 2]
    internal_frame_rate: float
    internal_frame_interval: float
    internal_line_rate: float
    internal_line_speed: float
    image_width: int
    image_height: int
    image_rowbytes: int
    image_framebytes: int
    image_top_offset_bytes: int
    image_bit_depth_alignment: Literal[1, 2]
    system_alive: Literal[1, 2]
    cc2_on_framegrabber: Literal[1, 2]
    number_of_channel: int
    attach_buffer_target: Literal[1, 2]
    number_of_target_per_attachbuffer: int


assert PropertyDict({name: 0 for name in get_args(Props)})  # type: ignore[misc]


class DCAMPROP_TYPES(IntEnum):
    NONE = 0b00
    MODE = 0b01
    LONG = 0b10
    REAL = 0b11


class DCAM_PARAM_PROPERTYATTR(Structure):
    _fields_ = [
        # /* input parameters */
        ("cbSize", c_int32),
        ("iProp", c_int32),
        ("option", c_int32),
        ("iReserved1", c_int32),
        # /* output parameters */
        ("attribute", c_int32),
        ("iGroup", c_int32),
        ("iUnit", c_int32),
        ("attribute2", c_int32),
        ("valuemin", c_double),
        ("valuemax", c_double),
        ("valuestep", c_double),
        ("valuedefault", c_double),
        ("nMaxChannel", c_int32),
        ("iReserved3", c_int32),
        ("nMaxView", c_int32),
        ("iProp_NumberOfElement", c_int32),
        ("iProp_ArrayBase", c_int32),
        ("iPropStep_Element", c_int32),
    ]

    @classmethod
    def from_id(cls, id_: c_int32) -> DCAM_PARAM_PROPERTYATTR:
        attr = cls()
        attr.cbSize = sizeof(attr)
        attr.iProp = id_
        return attr
