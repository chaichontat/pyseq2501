from __future__ import annotations

from ctypes import Structure, addressof, c_char_p, c_double, c_int32, c_void_p, create_string_buffer, sizeof
from dataclasses import dataclass
from enum import IntEnum
from logging import getLogger
from typing import Literal, TypedDict, get_args

logger = getLogger(__name__)

# fmt: off
DCAMPROP_TYPE_MASK      = 0x0000000F
DCAMPROP_OPTION_NEXT    = 0x01000000
DCAMPROP_OPTION_NEAREST = 0x80000000
# fmt: on


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


class PropTypes(IntEnum):
    NONE = 0b00
    MODE = 0b01
    LONG = 0b10
    REAL = 0b11


PrecomputedPropTypes: dict[Props, PropTypes] = dict(
    sensor_mode=PropTypes.MODE,
    sensor_mode_line_bundle_height=PropTypes.LONG,
    colortype=PropTypes.MODE,
    bit_per_channel=PropTypes.LONG,
    trigger_source=PropTypes.MODE,
    trigger_mode=PropTypes.MODE,
    trigger_active=PropTypes.MODE,
    trigger_polarity=PropTypes.MODE,
    trigger_connector=PropTypes.MODE,
    exposure_time=PropTypes.REAL,
    contrast_gain=PropTypes.LONG,
    primary_buffer_mode=PropTypes.MODE,
    binning=PropTypes.MODE,
    subarray_hpos=PropTypes.LONG,
    subarray_hsize=PropTypes.LONG,
    subarray_vpos=PropTypes.LONG,
    subarray_vsize=PropTypes.LONG,
    subarray_mode=PropTypes.MODE,
    number_of_partial_area=PropTypes.LONG,
    partial_area_vpos=PropTypes.LONG,
    partial_area_vsize=PropTypes.LONG,
    timing_readout_time=PropTypes.REAL,
    timing_cyclic_trigger_period=PropTypes.REAL,
    timing_min_trigger_blanking=PropTypes.REAL,
    timing_min_trigger_interval=PropTypes.REAL,
    timing_exposure=PropTypes.MODE,
    internal_frame_rate=PropTypes.REAL,
    internal_frame_interval=PropTypes.REAL,
    internal_line_rate=PropTypes.REAL,
    internal_line_speed=PropTypes.REAL,
    image_width=PropTypes.LONG,
    image_height=PropTypes.LONG,
    image_rowbytes=PropTypes.LONG,
    image_framebytes=PropTypes.LONG,
    image_top_offset_bytes=PropTypes.LONG,
    image_bit_depth_alignment=PropTypes.MODE,
    system_alive=PropTypes.MODE,
    cc2_on_framegrabber=PropTypes.MODE,
    number_of_channel=PropTypes.LONG,
    attach_buffer_target=PropTypes.MODE,
    number_of_target_per_attachbuffer=PropTypes.LONG,
)  # type: ignore


@dataclass(frozen=True)
class DCAMParamPropertyAttr:
    # /* input parameters */
    cbSize: int
    iProp: int
    option: int
    iReserved1: int
    # /* output parameters */
    attribute: int
    iGroup: int
    iUnit: int
    attribute2: int
    valuemin: float
    valuemax: float
    valuestep: float
    valuedefault: float
    nMaxChannel: int
    iReserved3: int
    nMaxView: int
    iProp_NumberOfElement: int
    iProp_ArrayBase: int
    iPropStep_Element: int

    @property
    def type_(self) -> PropTypes:
        return PropTypes(self.attribute & DCAMPROP_TYPE_MASK)


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

    def to_dataclass(self) -> DCAMParamPropertyAttr:
        dic = {f: getattr(self, f) for f, _ in self._fields_}
        return DCAMParamPropertyAttr(**dic)


class DCAM_PARAM_PROPERTYVALUETEXT(Structure):
    _fields_ = [
        ("cbSize", c_int32),
        ("iProp", c_int32),
        ("value", c_double),
        ("text", c_char_p),
        ("textbytes", c_int32),
    ]

    def __init__(self, prop_attr: DCAMParamPropertyAttr) -> None:
        super().__init__()

        c_buf_len = 64
        self.c_buf = create_string_buffer(c_buf_len)  # Prevents garbage collection.

        self.cbSize = c_int32(sizeof(self))
        self.iProp = c_int32(prop_attr.iProp)
        self.value = c_double(prop_attr.valuemin)
        self.text = c_char_p(addressof(self.c_buf))
        self.textbytes = c_int32(c_buf_len)
