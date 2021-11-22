from __future__ import annotations

import ctypes
from ctypes import byref, c_double, c_int32
from dataclasses import dataclass
from logging import getLogger
from typing import Optional, get_args

from src.imaging.camera.dcam_mode_key import MODE_KEY, get_mode_key
from src.imaging.camera.dcam_types import (DCAM_PARAM_PROPERTYATTR,
                                           DCAMPROP_OPTION_NEAREST,
                                           DCAMPROP_OPTION_NEXT,
                                           CheckedDCAMAPI,
                                           DCAMParamPropertyAttr,
                                           DCAMReturnedZero, Handle,
                                           PrecomputedPropTypes, Props,
                                           PropTypes)

# /* DCAM-API 3.0 */
# BOOL DCAMAPI dcam_getpropertyattr	( HDCAM h, DCAM_PROPERTYATTR* param );
# BOOL DCAMAPI dcam_getpropertyvalue	( HDCAM h, int32 iProp, double* pValue );
# BOOL DCAMAPI dcam_setpropertyvalue	( HDCAM h, int32 iProp, double  fValue );

# BOOL DCAMAPI dcam_setgetpropertyvalue(HDCAM h, int32 iProp, double* pValue, int32 option DCAM_DEFAULT_ARG );
# BOOL DCAMAPI dcam_querypropertyvalue( HDCAM h, int32 iProp, double* pValue, int32 option DCAM_DEFAULT_ARG );

# BOOL DCAMAPI dcam_getnextpropertyid	( HDCAM h, int32* pProp, int32 option DCAM_DEFAULT_ARG );
# BOOL DCAMAPI dcam_getpropertyname	( HDCAM h, int32 iProp, char* text, int32 textbytes );
# BOOL DCAMAPI dcam_getpropertyvaluetext( HDCAM h, DCAM_PROPERTYVALUETEXT* param );

logger = getLogger("DCAMprops")

API = CheckedDCAMAPI()
DCAM_DEFAULT_ARG = 0


@dataclass
class DCAMProperty:
    name: Props
    attr: DCAMParamPropertyAttr
    value: float

    @property
    def id_(self) -> c_int32:
        return c_int32(self.attr.iProp)

    @property
    def type_(self) -> PropTypes:
        return self.attr.type_

    @property
    def mode_key(self) -> Optional[dict[bytes, int]]:
        return MODE_KEY[self.name]

    def __str__(self) -> str:
        return f"{self.name}: {self.value}"


class DCAMDict:
    _TYPES = PrecomputedPropTypes

    def __init__(self, handle: Handle, prop_dict: dict[Props, DCAMProperty]):
        self.handle = handle
        self._dict = prop_dict

    def __getitem__(self, key: Props) -> float:
        return self._dict[key].value

    def __setitem__(self, key: Props, item: int | float) -> None:
        prop = self._dict[key]
        # TODO: Check writable.
        min_val: float = prop.attr.valuemin
        max_val: float = prop.attr.valuemax
        if not (min_val <= item <= max_val):
            raise ValueError(f"Out of range for {key}. Given {item}, range is [{min_val}, {max_val}].")

        value = ctypes.c_double(item)
        API.dcam_setgetpropertyvalue(self.handle, prop.id_, byref(value), c_int32(DCAM_DEFAULT_ARG))
        # assert value == prop.value  # Function returns previously stored value.

        prop.value = ctypes.c_double(item).value

    def __str__(self) -> str:
        return f"Properties: {{{', '.join(map(str, self._dict.values()))}}}"

    @staticmethod
    def to_snake_case(s: bytes):
        return s.lower().decode("utf-8").replace(" ", "_")

    @classmethod
    def from_dcam(cls, h: Handle, check_precomputed=True):
        c_buf_len = 64
        dcam_props: dict[Props, DCAMProperty] = {}

        this_name = ctypes.create_string_buffer(c_buf_len)
        this_id = c_int32(0)

        try:
            # Reset counter to start.
            API.dcam_getnextpropertyid(h, byref(this_id), c_int32(DCAMPROP_OPTION_NEAREST))
        except DCAMReturnedZero:
            pass

        while True:
            try:
                API.dcam_getnextpropertyid(h, byref(this_id), c_int32(DCAMPROP_OPTION_NEXT))
            except DCAMReturnedZero:
                break  # All properties retrieved.

            API.dcam_getpropertyname(h, this_id, this_name, c_int32(c_buf_len))

            # Get attr.
            this_attr = DCAM_PARAM_PROPERTYATTR.from_id(this_id)
            API.dcam_getpropertyattr(h, byref(this_attr))

            # Get value.
            this_value = c_double(0)
            API.dcam_getpropertyvalue(h, this_id, byref(this_value))
            name = cls.to_snake_case(this_name.value)
            dcam_props[name] = DCAMProperty(name, this_attr.to_dataclass(), this_value.value)

            if check_precomputed:
                assert dcam_props[name].type_ == dcam_props[name].attr.type_
                print(dcam_props[name].mode_key)
                print("gnd", gnd := get_mode_key(h, dcam_props[name].attr))
                # assert dcam_props[name].mode_key == gnd

        assert all(x in dcam_props.keys() for x in get_args(Props))
        return DCAMDict(h, dcam_props)
