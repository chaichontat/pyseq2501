from ctypes import WinDLL, _CArgObject, byref, c_char_p, c_double, c_int32, c_ubyte, c_uint32
from typing import Literal

from src.imaging.camera.dcam import DCAM_CAPTUREMODE_SNAP

# DCAM_CAPTUREMODE_SNAP		= 0,
# DCAM_CAPTUREMODE_SEQUENCE	= 1,
DCAM_DEFAULT_ARG = c_int32(0)
DCAM_DEFAULT_ARG_p = byref(c_int32(0))
Handle = c_void_p
DCAM_CAPTUREMODE = Literal[c_int32(0), c_int32(1)]
c_void_p = _CArgObject
c_void_pp = _CArgObject
c_int32_p = _CArgObject
c_uint32_p = _CArgObject
c_double_p = _CArgObject
c_ubyte_pp = _CArgObject
DCAM_PARAM_PROPERTYVALUETEXT_p = _CArgObject
DCAM_PROPERTYATTR_p = _CArgObject

class DCAMAPI(WinDLL):
    # /*** --- parameters --- ***/
    def dcam_queryupdate(
        self, h: Handle, pFlag: c_int32_p, reserved: c_uint32_p = DCAM_DEFAULT_ARG_p
    ) -> bool: ...
    def dcam_getbinning(self, h: Handle, pBinning: c_int32_p) -> bool: ...
    def dcam_getexposuretime(self, h: Handle, pSec: c_double_p) -> bool: ...
    def dcam_gettriggermode(self, h: Handle, pMode: c_int32_p) -> bool: ...
    def dcam_gettriggerpolarity(self, h: Handle, pPolarity: c_int32_p) -> bool: ...
    def dcam_setbinning(self, h: Handle, binning: c_int32) -> bool: ...
    def dcam_setexposuretime(self, h: Handle, sec: c_double) -> bool: ...
    def dcam_settriggermode(self, h: Handle, mode: c_int32) -> bool: ...
    def dcam_settriggerpolarity(self, h: Handle, polarity: c_int32) -> bool: ...
    # /*** --- capturing --- ***/
    def dcam_precapture(self, h: Handle, mode: DCAM_CAPTUREMODE) -> bool: ...
    def dcam_getdatarange(self, h: Handle, pMax: c_int32_p, pMin: c_int32_p = DCAM_DEFAULT_ARG_p) -> bool: ...
    def dcam_getdataframebytes(self, h: Handle, pSize: c_int32_p) -> bool: ...
    def dcam_allocframe(self, h: Handle, framecount: c_int32) -> bool: ...
    def dcam_getframecount(self, h: Handle, pFrame: c_int32_p) -> bool: ...
    def dcam_capture(self, h: Handle) -> bool: ...
    def dcam_idle(self, h: Handle) -> bool: ...
    def dcam_wait(
        self,
        h: Handle,
        pCode: c_int32_p,
        timeout: c_uint32_p = DCAM_DEFAULT_ARG_p,
        abortsignal: Handle = DCAM_DEFAULT_ARG_p,
    ) -> bool: ...
    def dcam_getstatus(self, h: Handle, pStatus: c_int32_p) -> bool: ...
    def dcam_gettransferinfo(
        self, h: Handle, pNewestFrameIndex: c_int32_p, pFrameCount: c_int32_p
    ) -> bool: ...
    def dcam_freeframe(self, h: Handle) -> bool: ...
    # /*** --- user memory support --- ***/
    def dcam_attachbuffer(self, h: Handle, frames: c_void_pp, size: c_uint32_p) -> bool: ...
    def dcam_releasebuffer(self, h: Handle) -> bool: ...
    # /*** --- data transfer --- ***/
    def dcam_lockdata(self, h: Handle, pTop: c_void_pp, pRowbytes: c_int32_p, frame: c_int32) -> bool: ...
    def dcam_lockbits(self, h: Handle, pTop: c_ubyte_pp, pRowbytes: c_int32_p, frame: c_int32) -> bool: ...
    def dcam_unlockdata(self, h: Handle) -> bool: ...
    def dcam_unlockbits(self, h: Handle) -> bool: ...
    # /*** --- LUT --- ***/
    def dcam_setbitsinputlutrange(
        self, h: Handle, inMax: c_int32, inMin: c_int32 = DCAM_DEFAULT_ARG
    ) -> bool: ...
    def dcam_setbitsoutputlutrange(
        self, h: Handle, outMax: c_ubyte, outMin: c_int32 = DCAM_DEFAULT_ARG
    ) -> bool: ...
    # /*** --- extended --- ***/
    def dcam_extended(self, h: Handle, iCmd: c_uint32, param: c_void_p, size: c_uint32_p) -> bool: ...
    # /*** --- software trigger --- ***/
    def dcam_firetrigger(self, h: Handle) -> bool: ...
    def dcam_getpropertyattr(self, h: Handle, param: DCAM_PROPERTYATTR_p) -> bool: ...
    def dcam_getpropertyvalue(self, h: Handle, iProp: c_int32, pValue: c_double_p) -> bool: ...
    def dcam_setpropertyvalue(self, h: Handle, iProp: c_int32, fValue: c_double) -> bool: ...
    def dcam_setgetpropertyvalue(
        self, h: Handle, iProp: c_int32, pValue: c_double_p, option: c_int32 = DCAM_DEFAULT_ARG
    ) -> bool: ...
    def dcam_querypropertyvalue(
        self, h: Handle, iProp: c_int32, pValue: c_double_p, option: c_int32 = DCAM_DEFAULT_ARG
    ) -> bool: ...
    def dcam_getnextpropertyid(
        self, h: Handle, pProp: c_int32_p, option: c_int32 = DCAM_DEFAULT_ARG
    ) -> bool: ...
    def dcam_getpropertyname(self, h: Handle, iProp: c_int32, text: c_char_p, textbytes: c_int32) -> bool: ...
    def dcam_getpropertyvaluetext(self, h: Handle, param: DCAM_PARAM_PROPERTYVALUETEXT_p) -> bool: ...
