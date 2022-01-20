from __future__ import annotations

from ctypes import c_double, c_int32, pointer
from logging import getLogger
from typing import Optional, cast

from . import API
from .dcam_api import DCAMReturnedZero
from .dcam_types import (
    DCAM_PARAM_PROPERTYVALUETEXT,
    DCAMPROP_OPTION_NEXT,
    DCAMParamPropertyAttr,
    Handle,
    Props,
)

logger = getLogger(__name__)
DCAMPROP_ATTR_HASVALUETEXT = int("0x10000000", 0)


MODE_KEY: dict[Props, Optional[dict[str, int]]] = {
    "sensor_mode": {"AREA": 1, "LINE": 3, "TDI": 4, "PARTIAL AREA": 6},
    "sensor_mode_line_bundle_height": None,
    "colortype": {"B/W": 1},
    "bit_per_channel": None,
    "trigger_source": {"INTERNAL": 1, "EXTERNAL": 2},
    "trigger_mode": {"NORMAL": 1},
    "trigger_active": {"SYNCREADOUT": 3},
    "trigger_polarity": {"NEGATIVE": 1, "POSITIVE": 2},
    "trigger_connector": {"INTERFACE": 1, "BNC": 2},
    "exposure_time": None,
    "contrast_gain": None,
    "primary_buffer_mode": {"AUTO": 1, "DIRECT": 2},
    "binning": {"1x1": 1, "2x2": 2},
    "subarray_hpos": None,
    "subarray_hsize": None,
    "subarray_vpos": None,
    "subarray_vsize": None,
    "subarray_mode": {"OFF": 1, "ON": 2},
    "number_of_partial_area": None,
    "partial_area_vpos": None,
    "partial_area_vsize": None,
    "timing_readout_time": None,
    "timing_cyclic_trigger_period": None,
    "timing_min_trigger_blanking": None,
    "timing_min_trigger_interval": None,
    "timing_exposure": {"AFTER READOUT": 1, "OVERLAP READOUT": 2},
    "internal_frame_rate": None,
    "internal_frame_interval": None,
    "internal_line_rate": None,
    "internal_line_speed": None,
    "image_width": None,
    "image_height": None,
    "image_rowbytes": None,
    "image_framebytes": None,
    "image_top_offset_bytes": None,
    "image_bit_depth_alignment": {"LS": 1, "MS": 2},
    "system_alive": {"OFFLINE": 1, "ONLINE": 2},
    "cc2_on_framegrabber": {"OFF": 1, "ON": 2},
    "number_of_channel": None,
    "attach_buffer_target": {"EACH FRAME": 1, "EVERY CHANNEL": 2},
    "number_of_target_per_attachbuffer": None,
}


def get_mode_key(handle: Handle, prop_attr: DCAMParamPropertyAttr) -> Optional[dict[str, int]]:
    if not (prop_attr.attribute & DCAMPROP_ATTR_HASVALUETEXT):
        return None

    prop_text = DCAM_PARAM_PROPERTYVALUETEXT(prop_attr)  # type: ignore
    v = c_double(prop_attr.valuemin)

    out: dict[str, int] = {}

    while True:
        # Get text of current value.
        API.dcam_getpropertyvaluetext(handle, pointer(prop_text))
        out[cast(bytes, prop_text.text).decode()] = int(v.value)

        # Get next value.
        try:
            API.dcam_querypropertyvalue(
                handle,
                c_int32(prop_attr.iProp),
                pointer(v),
                c_int32(DCAMPROP_OPTION_NEXT),
            )
            prop_text.value = v
        except DCAMReturnedZero:  # Done
            break
    return out
