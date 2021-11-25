from ctypes import Array, WinDLL, _CArgObject, byref, c_char, c_double, c_int32, c_ubyte, c_uint32, c_void_p
from typing import Literal

# DCAM_CAPTUREMODE_SNAP		= 0,
# DCAM_CAPTUREMODE_SEQUENCE	= 1,
DCAM_DEFAULT_ARG = c_int32(0)
DCAM_DEFAULT_ARG_p = byref(c_int32(0))
Handle = c_void_p
DCAM_CAPTUREMODE = Literal[c_int32(0), c_int32(1)]
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
    def dcam_getbinning(self, h: Handle, pBinning: c_int32_p) -> bool:
        """This will return the current binning mode of the camera."""
    def dcam_getexposuretime(self, h: Handle, pSec: c_double_p) -> bool:
        """This returns the value of the current exposure time in seconds."""
    def dcam_gettriggermode(self, h: Handle, pMode: c_int32_p) -> bool:
        """This returns the value of the current trigger mode. The value returned will be numeric and it may be necessary to use the global variables to process this data."""
    def dcam_gettriggerpolarity(self, h: Handle, pPolarity: c_int32_p) -> bool:
        """This returns the value of the current polarity. This function will fail if the camera does not support external trigger."""
    def dcam_setbinning(self, h: Handle, binning: c_int32) -> bool:
        """This function will adjust the binning of the camera. Adjusting the binning will also change the output data size, but the pixel depth will remain the same."""
    def dcam_setexposuretime(self, h: Handle, sec: c_double) -> bool:
        """This allows you to modify the exposure time in seconds of the camera. Depending on the camera, the exposure time that you specify may not be the same exposure time actually set. If necessary, check the actual time set using DCAM_GETEXPOSURETIME."""
    def dcam_settriggermode(self, h: Handle, mode: c_int32) -> bool:
        """This function allows you to switch the current trigger mode. Create a constant or control from the Mode terminal to get a list of trigger mode IDs. However, although they are listed, it may or may not be a valid ID for your camera."""
    def dcam_settriggerpolarity(self, h: Handle, polarity: c_int32) -> bool:
        """This will select the polarity of the trigger if the camera has been set to external trigger mode. This function will fail if the camera does not support external trigger. Create a constant or control from the Polarity terminal to get a list of valid IDs."""
    # /*** --- capturing --- ***/
    def dcam_precapture(self, h: Handle, mode: DCAM_CAPTUREMODE) -> bool:
        """Sets the capture mode and prepares resources for capturing. This also changes the camera status to STABLE state. Create a constant or control from the Capture Mode terminal to get a list of valid IDs."""
    def dcam_getdatarange(self, h: Handle, pMax: c_int32_p, pMin: c_int32_p = DCAM_DEFAULT_ARG_p) -> bool:
        """This function will return the minimum and maximum values possible for the data pixels."""
    def dcam_getdataframebytes(self, h: Handle, pSize: c_int32_p) -> bool:
        """This determines the amount of bytes required for a single frame of data. This is useful when using DCAM_ATTACHBUFFER."""
    def dcam_allocframe(self, h: Handle, framecount: c_int32) -> bool:
        """Allocates the proper amount of memory for a data buffer depending on the number of frames requested and changes the camera status from STABLE to READY. Capturing does not start at this time. This function will fail if called while camera is not in STABLE state."""
    def dcam_getframecount(self, h: Handle, pFrame: c_int32_p) -> bool:
        """Returns the number of frames allocated in memory by either DCAM_ALLOCFRAME or by DCAM_ATTACHBUFFER. This function will fail is no frames have been allocated."""
    def dcam_capture(self, h: Handle) -> bool:
        """This starts capturing images. Camera status must be READY before using this function. If the camera is in SEQUENCE mode, the camera will capture images repeatedly. If the camera is in SNAP mode, the camera will capture only the number of images for frames that were allocated."""
    def dcam_idle(self, h: Handle) -> bool:
        """This function will stop the capturing of images. If the camera is in BUSY state, it will set it to READY state."""
    def dcam_wait(
        self,
        h: Handle,
        pCode: c_int32_p,
        timeout: c_uint32_p = DCAM_DEFAULT_ARG_p,
        abortsignal: Handle | c_void_pp = DCAM_DEFAULT_ARG_p,
    ) -> bool: ...
    def dcam_getstatus(self, h: Handle, pStatus: c_int32_p) -> bool:
        """This returns the state of the current camera operation."""
    def dcam_gettransferinfo(
        self, h: Handle, pNewestFrameIndex: c_int32_p, pFrameCount: c_int32_p
    ) -> bool: ...
    def dcam_freeframe(self, h: Handle) -> bool:
        """This frees up the memory allocated from DCAM_ALLOCFRAME. Also sets the status of the camera from READY state to STABLE state. This will fail if the camera is in BUSY state when called."""
    # /*** --- user memory support --- ***/
    def dcam_attachbuffer(self, h: Handle, frames: c_void_pp, size: c_uint32_p) -> bool:
        """This allows the user to attach his/her own data buffer instead of using DCAM_ALLOCFRAME and using the DCAM buffer. This function accepts an array of pointers to image buffers. If used, this will take the place of DCAM_ALLOCFRAME and set the camera from STABLE to READY state."""
    def dcam_releasebuffer(self, h: Handle) -> bool:
        """This function works similar to DCAM_FREEFRAME except that this is used when using DCAM_ATTACHBUFFER. This will set the camera from READY to STABLE state."""
    # /*** --- data transfer --- ***/
    def dcam_lockdata(self, h: Handle, pTop: c_void_pp, pRowbytes: c_int32_p, frame: c_int32) -> bool:
        """This locks a frame in the data buffer that will be accessed by the user. When a frame is locked, the capture thread will not write to it. Calling this function will also unlock any existing locked frames. If you set the frame input as -1, you will lock the most recently received frame."""
    def dcam_lockbits(self, h: Handle, pTop: c_ubyte_pp, pRowbytes: c_int32_p, frame: c_int32) -> bool:
        """This works similar to DCAM_LOCKDATA except that the buffer data has been altered for display. For example, 16 bit images are converted to 8 bit images and flipped for easy use in Windows API functions. If you set the frame input as -1, you will lock the most recently received frame."""
    def dcam_unlockdata(self, h: Handle) -> bool:
        """If a framed has been locked by DCAM_LOCKDATA, this function will unlock it."""
    def dcam_unlockbits(self, h: Handle) -> bool:
        """If a framed has been locked by DCAM_LOCKBITS, this function will unlock it."""
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
    def dcam_getpropertyname(
        self, h: Handle, iProp: c_int32, text: Array[c_char], textbytes: c_int32
    ) -> bool: ...
    def dcam_getpropertyvaluetext(self, h: Handle, param: DCAM_PARAM_PROPERTYVALUETEXT_p) -> bool: ...