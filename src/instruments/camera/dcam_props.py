from __future__ import annotations

import ctypes
from ctypes import byref, c_double, c_int32
from dataclasses import dataclass
from enum import IntEnum
from typing import get_args

from src.instruments.camera.dcam_types import DCAM_PARAM_PROPERTYATTR, CheckedDCAMAPI, Handle, Props

# /* DCAM-API 3.0 */
# BOOL DCAMAPI dcam_getpropertyattr	( HDCAM h, DCAM_PROPERTYATTR* param );
# BOOL DCAMAPI dcam_getpropertyvalue	( HDCAM h, int32 iProp, double* pValue );
# BOOL DCAMAPI dcam_setpropertyvalue	( HDCAM h, int32 iProp, double  fValue );

# BOOL DCAMAPI dcam_setgetpropertyvalue(HDCAM h, int32 iProp, double* pValue, int32 option DCAM_DEFAULT_ARG );
# BOOL DCAMAPI dcam_querypropertyvalue( HDCAM h, int32 iProp, double* pValue, int32 option DCAM_DEFAULT_ARG );

# BOOL DCAMAPI dcam_getnextpropertyid	( HDCAM h, int32* pProp, int32 option DCAM_DEFAULT_ARG );
# BOOL DCAMAPI dcam_getpropertyname	( HDCAM h, int32 iProp, char* text, int32 textbytes );
# BOOL DCAMAPI dcam_getpropertyvaluetext( HDCAM h, DCAM_PROPERTYVALUETEXT* param );


API = CheckedDCAMAPI()
DCAM_DEFAULT_ARG = 0

DCAMPROP_OPTION_NEXT = int("0x01000000", 0)

DCAMERR_ERROR = 0
DCAMERR_NOERROR = 1


class DCAMPROP_TYPES(IntEnum):
    NONE = 0b00
    MODE = 0b01
    LONG = 0b10
    REAL = 0b11


def to_snake_case(s: bytes):
    return s.lower().decode("utf-8").replace(" ", "_")


@dataclass
class DCAMProperty:
    id_: c_int32
    attr: DCAM_PARAM_PROPERTYATTR
    value: c_double


class DCAMDict:
    def __init__(self, handle: Handle, prop_dict: dict[Props, DCAMProperty]):
        self.handle = handle
        self._dict = prop_dict

    def __getitem__(self, key: Props) -> float:
        return self._dict[key].value.value

    def __setitem__(self, key: Props, item: int | float) -> None:
        prop = self._dict[key]
        value = ctypes.c_double(item)
        min_val: float = prop.attr.valuemin.value
        max_val: float = prop.attr.valuemax.value
        if not (min_val <= item <= max_val):
            raise ValueError(f"Out of range for {key}. Given {item}, range is [{min_val}, {max_val}].")

        API.dcam_setgetpropertyvalue(self.handle, prop.id_, byref(value), c_int32(DCAM_DEFAULT_ARG))
        assert value == prop.value  # Function returns previously stored value.
        prop.value = ctypes.c_double(item)

    @classmethod
    def from_dcam(cls, h: Handle):
        c_buf_len = 64
        dcam_props: dict[Props, DCAMProperty] = {}

        this_name = ctypes.create_string_buffer(c_buf_len)
        this_id = c_int32(0)
        prev = c_int32(-1)
        while True:
            # Get ID.
            API.dcam_getnextpropertyid(h, byref(this_id), c_int32(DCAMPROP_OPTION_NEXT))
            API.dcam_getpropertyname(h, this_id, this_name, c_int32(c_buf_len))
            if this_id.value == prev:
                break

            # Get attr.
            this_attr = DCAM_PARAM_PROPERTYATTR.from_id(this_id)
            API.dcam_getpropertyattr(h, ctypes.byref(this_attr))

            # Get value.
            this_value = c_double(0)
            API.dcam_getpropertyvalue(h, this_id, ctypes.byref(this_value))

            dcam_props[to_snake_case(this_name.value)] = DCAMProperty(
                id_=this_id, attr=this_attr, value=this_value
            )

            prev = this_id

        assert all(x in dcam_props.keys() for x in get_args(Props))
        return DCAMDict(h, dcam_props)
