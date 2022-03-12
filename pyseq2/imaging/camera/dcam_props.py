from __future__ import annotations

import ctypes
import os
import threading
from ctypes import c_double, c_int32, pointer
from dataclasses import dataclass
from logging import getLogger
from typing import Iterator, MutableMapping, NoReturn, cast, get_args

import numpy as np

from . import API
from .dcam_api import DCAMReturnedZero
from .dcam_mode_key import get_mode_key
from .dcam_types import (
    DCAM_PARAM_PROPERTYATTR,
    DCAMPROP_OPTION_NEAREST,
    DCAMPROP_OPTION_NEXT,
    DCAMParamPropertyAttr,
    Handle,
    PrecomputedPropTypes,
    Props,
    PropTypes,
)
from pyseq2.utils.utils import IS_FAKE

# /* DCAM-API 3.0 */
# BOOL DCAMAPI dcam_getpropertyattr	( HDCAM h, DCAM_PROPERTYATTR* param );
# BOOL DCAMAPI dcam_getpropertyvalue	( HDCAM h, int32 iProp, double* pValue );
# BOOL DCAMAPI dcam_setpropertyvalue	( HDCAM h, int32 iProp, double  fValue );

# BOOL DCAMAPI dcam_setgetpropertyvalue(HDCAM h, int32 iProp, double* pValue, int32 option DCAM_DEFAULT_ARG );
# BOOL DCAMAPI dcam_querypropertyvalue( HDCAM h, int32 iProp, double* pValue, int32 option DCAM_DEFAULT_ARG );

# BOOL DCAMAPI dcam_getnextpropertyid	( HDCAM h, int32* pProp, int32 option DCAM_DEFAULT_ARG );
# BOOL DCAMAPI dcam_getpropertyname	( HDCAM h, int32 iProp, char* text, int32 textbytes );
# BOOL DCAMAPI dcam_getpropertyvaluetext( HDCAM h, DCAM_PROPERTYVALUETEXT* param );

logger = getLogger(__name__)
LOCK = threading.Lock()
DCAM_DEFAULT_ARG = 0


@dataclass
class DCAMProperty:
    name: Props
    attr: DCAMParamPropertyAttr
    value: float
    mode_key: None | dict[str, int]  # None if not mode.

    @staticmethod
    def get_attr_val(h: Handle, id_: c_int32) -> tuple[DCAMParamPropertyAttr, float]:
        attr = DCAM_PARAM_PROPERTYATTR.from_id(id_)
        API.dcam_getpropertyattr(h, pointer(attr))
        attr = attr.to_dataclass()

        value = c_double(0)
        API.dcam_getpropertyvalue(h, id_, pointer(value))
        return attr, value.value

    @classmethod
    def from_dcam(cls, h: Handle, name: Props, id_: c_int32):
        attr, value = DCAMProperty.get_attr_val(h, id_)
        return cls(name, attr, value, get_mode_key(h, attr))

    @property
    def id_(self) -> c_int32:
        return c_int32(self.attr.iProp)

    @property
    def type_(self) -> PropTypes:
        return self.attr.type_

    def refresh(self, handle: Handle):
        self.attr, self.value = self.get_attr_val(handle, self.id_)

    def __str__(self) -> str:
        return f"{self.name}: {self.value}"

    def __eq__(self, __o: DCAMProperty) -> bool:
        return str(self) == str(__o)


class DCAMDict(MutableMapping[Props, float]):
    _TYPES = PrecomputedPropTypes

    def __init__(self, handle: Handle, prop_dict: dict[Props, DCAMProperty]):
        self.handle = handle
        self._dict = prop_dict

    def __getitem__(self, name: Props) -> float:
        return self._dict[name].value

    def __setitem__(self, name: Props, value: float) -> None:
        if IS_FAKE():
            return

        with LOCK:
            prop = self._dict[name]
            # TODO: Check writable.
            min_val: float = prop.attr.valuemin
            max_val: float = prop.attr.valuemax
            if not (min_val <= value <= max_val):
                raise ValueError(f"Out of range for {name}. Given {value}, range is [{min_val}, {max_val}].")

            to_set = ctypes.c_double(value)
            API.dcam_setgetpropertyvalue(self.handle, prop.id_, pointer(to_set), c_int32(DCAM_DEFAULT_ARG))
            logger.info(f"Set {name} to {value}.")
            self.refresh()
            assert np.allclose(
                self[name], value
            ), f"Value in DCAM not same as target. Expected {value}, got {self[name]}."

    def __delitem__(self, _: Props) -> NoReturn:
        raise Exception("Cannot remove properties!")

    def __iter__(self) -> Iterator[Props]:
        return iter(self._dict)

    def __len__(self) -> int:
        return len(self._dict)

    def __str__(self) -> str:
        return f"Properties: {{{', '.join(map(str, self._dict.values()))}}}"

    def __eq__(self, __o: object) -> bool:
        if not isinstance(__o, DCAMDict):
            return False
        return self._dict == __o._dict

    def refresh(self) -> None:
        [v.refresh(self.handle) for v in self._dict.values()]
        logger.debug("DCAMProp refreshed.")

    @staticmethod
    def to_snake_case(s: bytes) -> str:  # pragma: no cover
        return s.lower().decode("utf-8").replace(" ", "_")

    @staticmethod
    def retrieve_dcam(h: Handle) -> dict[Props, DCAMProperty]:
        c_buf_len = c_int32(64)
        dcam_props: dict[Props, DCAMProperty] = {}

        with LOCK:
            name_buf = ctypes.create_string_buffer(c_buf_len.value)
            this_id = c_int32(0)

            try:  # Reset counter to start.
                API.dcam_getnextpropertyid(h, pointer(this_id), c_int32(DCAMPROP_OPTION_NEAREST))
            except DCAMReturnedZero:
                pass

            while True:
                try:
                    API.dcam_getnextpropertyid(h, pointer(this_id), c_int32(DCAMPROP_OPTION_NEXT))
                except DCAMReturnedZero:
                    break  # All properties retrieved.

                API.dcam_getpropertyname(h, this_id, name_buf, c_buf_len)
                assert (this_name := cast(Props, DCAMDict.to_snake_case(name_buf.value))) in get_args(Props)
                dcam_props[this_name] = DCAMProperty.from_dcam(h, this_name, this_id)
            return dcam_props

    @classmethod
    def from_dcam(cls, h: Handle) -> DCAMDict:
        return cls(h, cls.retrieve_dcam(h))
