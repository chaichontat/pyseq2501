from __future__ import annotations

from ctypes import (
    Structure,
    addressof,
    byref,
    c_char_p,
    c_double,
    c_int32,
    c_uint32,
    create_string_buffer,
    sizeof,
)

from src.instruments.camera.dcam_types import (
    DCAM_PARAM_PROPERTYATTR,
    CheckedDCAMAPI,
    DCAMReturnedZero,
    Handle,
)

API = CheckedDCAMAPI()
DCAMPROP_ATTR_HASVALUETEXT = int("0x10000000", 0)
DCAMPROP_OPTION_NEXT = int("0x01000000", 0)


class DCAM_PARAM_PROPERTYVALUETEXT(Structure):
    """The dcam text property structure."""

    _fields_ = [
        ("cbSize", c_int32),
        ("iProp", c_int32),
        ("value", c_double),
        ("text", c_char_p),
        ("textbytes", c_int32),
    ]

    @classmethod
    def from_attr(cls, prop_id: c_uint32, v_min: c_double) -> DCAM_PARAM_PROPERTYVALUETEXT:
        t = cls()
        c_buf_len = 64
        c_buf = create_string_buffer(c_buf_len)
        t.cbSize = c_int32(sizeof(t))
        t.iProp = prop_id
        t.value = v_min
        t.text = addressof(c_buf)
        t.textbytes = c_buf_len
        return t


def get_prop_key(handle: Handle, prop_id: c_uint32, prop_attr: DCAM_PARAM_PROPERTYATTR) -> dict[str, int]:
    if not (prop_attr.attribute & DCAMPROP_ATTR_HASVALUETEXT):
        return {}

    v_min = c_double(prop_attr.valuemin)
    prop_text = DCAM_PARAM_PROPERTYVALUETEXT.from_attr(prop_id, v_min)

    out = {}
    while True:
        # Get text of current value.
        API.dcam_getpropertyvaluetext(handle, byref(prop_text))
        out[prop_text.text] = int(v_min.value)

        # Get next value.
        try:
            API.dcam_querypropertyvalue(handle, prop_id, byref(v_min), c_int32(DCAMPROP_OPTION_NEXT))
        except DCAMReturnedZero:
            break
    return out


# Real output.
#
# 'sensor_mode': {b'AREA': 1, b'LINE': 3, b'TDI': 4, b'PARTIAL AREA': 6}
# 'sensor_mode_line_bundle_height': {}
# 'colortype': {b'B/W': 1}
# 'bit_per_channel': {}
# 'trigger_source': {b'INTERNAL': 1, b'EXTERNAL': 2}
# 'trigger_mode': {b'NORMAL': 1}
# 'trigger_active': {b'SYNCREADOUT': 3}
# 'trigger_polarity': {b'NEGATIVE': 1, b'POSITIVE': 2}
# 'trigger_connector': {b'INTERFACE': 1, b'BNC': 2}
# 'exposure_time': {}
# 'contrast_gain': {}
# 'primary_buffer_mode': {b'AUTO': 1, b'DIRECT': 2}
# 'binning': {b'1x1': 1, b'2x2': 2}
# 'subarray_hpos': {}
# 'subarray_hsize': {}
# 'subarray_vpos': {}
# 'subarray_vsize': {}
# 'subarray_mode': {b'OFF': 1, b'ON': 2}
# 'number_of_partial_area': {}
# 'partial_area_vpos': {}
# 'partial_area_vsize': {}
# 'timing_readout_time': {}
# 'timing_cyclic_trigger_period': {}
# 'timing_min_trigger_blanking': {}
# 'timing_min_trigger_interval': {}
# 'timing_exposure': {b'AFTER READOUT': 1, b'OVERLAP READOUT': 2}
# 'internal_frame_rate': {}
# 'internal_frame_interval': {}
# 'internal_line_rate': {}
# 'internal_line_speed': {}
# 'image_width': {}
# 'image_height': {}
# 'image_rowbytes': {}
# 'image_framebytes': {}
# 'image_top_offset_bytes': {}
# 'image_bit_depth_alignment': {b'LSB': 1, b'MSB': 2}
# 'system_alive': {b'OFFLINE': 1, b'ONLINE': 2}
# 'cc2_on_framegrabber': {b'OFF': 1, b'ON': 2}
# 'number_of_channel': {}
# 'attach_buffer_target': {b'EACH FRAME': 1, b'EVERY CHANNEL': 2}
# 'number_of_target_per_attachbuffer': {}
