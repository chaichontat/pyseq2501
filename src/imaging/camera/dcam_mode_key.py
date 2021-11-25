from __future__ import annotations

from ctypes import (Structure, addressof, byref, c_char_p, c_double, c_int32,
                    create_string_buffer, sizeof)
from logging import getLogger
from typing import Optional

from . import API
from .dcam_types import (DCAMPROP_OPTION_NEXT, DCAMParamPropertyAttr,
                         DCAMReturnedZero, Handle, Props)

logger = getLogger("DCAMmodekey")

DCAMPROP_ATTR_HASVALUETEXT = int("0x10000000", 0)


MODE_KEY: dict[Props, Optional[dict[bytes, int]]] = {
    "sensor_mode": {b"AREA": 1, b"LINE": 3, b"TDI": 4, b"PARTIAL AREA": 6},
    "sensor_mode_line_bundle_height": None,
    "colortype": {b"B/W": 1},
    "bit_per_channel": None,
    "trigger_source": {b"INTERNAL": 1, b"EXTERNAL": 2},
    "trigger_mode": {b"NORMAL": 1},
    "trigger_active": {b"SYNCREADOUT": 3},
    "trigger_polarity": {b"NEGATIVE": 1, b"POSITIVE": 2},
    "trigger_connector": {b"INTERFACE": 1, b"BNC": 2},
    "exposure_time": None,
    "contrast_gain": None,
    "primary_buffer_mode": {b"AUTO": 1, b"DIRECT": 2},
    "binning": {b"1x1": 1, b"2x2": 2},
    "subarray_hpos": None,
    "subarray_hsize": None,
    "subarray_vpos": None,
    "subarray_vsize": None,
    "subarray_mode": {b"OFF": 1, b"ON": 2},
    "number_of_partial_area": None,
    "partial_area_vpos": None,
    "partial_area_vsize": None,
    "timing_readout_time": None,
    "timing_cyclic_trigger_period": None,
    "timing_min_trigger_blanking": None,
    "timing_min_trigger_interval": None,
    "timing_exposure": {b"AFTER READOUT": 1, b"OVERLAP READOUT": 2},
    "internal_frame_rate": None,
    "internal_frame_interval": None,
    "internal_line_rate": None,
    "internal_line_speed": None,
    "image_width": None,
    "image_height": None,
    "image_rowbytes": None,
    "image_framebytes": None,
    "image_top_offset_bytes": None,
    "image_bit_depth_alignment": {b"LSB": 1, b"MSB": 2},
    "system_alive": {b"OFFLINE": 1, b"ONLINE": 2},
    "cc2_on_framegrabber": {b"OFF": 1, b"ON": 2},
    "number_of_channel": None,
    "attach_buffer_target": {b"EACH FRAME": 1, b"EVERY CHANNEL": 2},
    "number_of_target_per_attachbuffer": None,
}


class DCAM_PARAM_PROPERTYVALUETEXT(Structure):
    _fields_ = [
        ("cbSize", c_int32),
        ("iProp", c_int32),
        ("value", c_double),
        ("text", c_char_p),
        ("textbytes", c_int32),
    ]

    @classmethod
    def from_attr(cls, prop_attr: DCAMParamPropertyAttr) -> DCAM_PARAM_PROPERTYVALUETEXT:
        c_buf_len = 64
        c_buf = create_string_buffer(c_buf_len)

        t = cls()
        t.cbSize = c_int32(sizeof(t))
        t.iProp = c_int32(prop_attr.iProp)
        t.value = c_double(prop_attr.valuemin)
        t.text = addressof(c_buf)
        t.textbytes = c_buf_len
        return t


def get_mode_key(handle: Handle, prop_attr: DCAMParamPropertyAttr) -> Optional[dict[str, int]]:
    # TODO: Weird bug Output: {b'LFF': 1, b'ON': 2} Real:{b'OFF': 1, b'ON': 2} 1st char shifted by 3.
    if not (prop_attr.attribute & DCAMPROP_ATTR_HASVALUETEXT):
        return None

    prop_text = DCAM_PARAM_PROPERTYVALUETEXT.from_attr(prop_attr)
    v = c_double(prop_attr.valuemin)

    out = {}

    while True:
        # Get text of current value.
        API.dcam_getpropertyvaluetext(handle, byref(prop_text))
        out[prop_text.text] = int(v.value)

        # Get next value.
        try:
            API.dcam_querypropertyvalue(
                handle, c_int32(prop_attr.iProp), byref(v), c_int32(DCAMPROP_OPTION_NEXT)
            )
            prop_text.value = v
        except DCAMReturnedZero:  # Done
            break
    return out
