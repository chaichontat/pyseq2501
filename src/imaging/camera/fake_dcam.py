from ctypes import POINTER, Array, c_char, c_char_p, c_double, c_int32, c_ubyte, c_uint32, c_void_p, pointer
from typing import Any, Generic, Optional, TypeVar

import numpy as np

from .dcam_types import DCAM_PARAM_PROPERTYATTR, DCAM_PARAM_PROPERTYVALUETEXT, Handle

DCAM_DEFAULT_ARG = c_int32(0)
DCAM_DEFAULT_ARG_p = pointer(DCAM_DEFAULT_ARG)
_CT = TypeVar("_CT")


class pointer(Generic[_CT]):
    contents: _CT


class FakeAPI:
    def __init__(self) -> None:
        self.fc = 0
        self.ready = 0
        self.tm = 4

    # TODO Missing functions in dcamapi3.h
    def dcam_init(self, reserved1: c_void_p, pCount: pointer[c_int32], option: c_char_p) -> bool:
        return True

    def dcam_open(self, h: pointer[Handle], index: c_int32, reserved: Optional[pointer[Any]]) -> bool:
        return True

    # /*** --- parameters --- ***/
    def dcam_queryupdate(self, h: Handle, pFlag: pointer[c_int32], reserved: pointer[c_int32]) -> bool:
        return False

    def dcam_getbinning(self, h: Handle, pBinning: pointer[c_int32]) -> bool:
        """This will return the current binning mode of the camera."""
        return False

    def dcam_getexposuretime(self, h: Handle, pSec: pointer[c_double]) -> bool:
        """This returns the value of the current exposure time in seconds."""
        return False

    def dcam_gettriggermode(self, h: Handle, pMode: pointer[c_int32]) -> bool:
        """This returns the value of the current trigger mode. The value returned will be numeric and it may be necessary to use the global variables to process this data."""
        pMode.contents.value = self.tm
        return True

    def dcam_gettriggerpolarity(self, h: Handle, pPolarity: pointer[c_int32]) -> bool:
        """This returns the value of the current polarity. This function will fail if the camera does not support external trigger."""
        return False

    def dcam_setbinning(self, h: Handle, binning: c_int32) -> bool:
        """This function will adjust the binning of the camera. Adjusting the binning will also change the output data size, but the pixel depth will remain the same."""
        return False

    def dcam_setexposuretime(self, h: Handle, sec: c_double) -> bool:
        """This allows you to modify the exposure time in seconds of the camera. Depending on the camera, the exposure time that you specify may not be the same exposure time actually set. If necessary, check the actual time set using DCAM_GETEXPOSURETIME."""
        return False

    def dcam_settriggermode(self, h: Handle, mode: c_int32) -> bool:
        """This function allows you to switch the current trigger mode. Create a constant or control from the Mode terminal to get a list of trigger mode IDs. However, although they are listed, it may or may not be a valid ID for your camera."""
        return False

    def dcam_settriggerpolarity(self, h: Handle, polarity: c_int32) -> bool:
        """This will select the polarity of the trigger if the camera has been set to external trigger mode. This function will fail if the camera does not support external trigger. Create a constant or control from the Polarity terminal to get a list of valid IDs."""
        return False

    # /*** --- capturing --- ***/
    def dcam_precapture(self, h: Handle, mode: c_int32) -> bool:
        """Sets the capture mode and prepares resources for capturing. This also changes the camera status to STABLE state. Create a constant or control from the Capture Mode terminal to get a list of valid IDs."""
        return True

    def dcam_getdatarange(
        self,
        h: Handle,
        pMax: pointer[c_int32],
        pMin: pointer[c_int32],
    ) -> bool:
        """This function will return the minimum and maximum values possible for the data pixels."""
        return False

    def dcam_getdataframebytes(self, h: Handle, pSize: pointer[c_int32]) -> bool:
        """This determines the amount of bytes required for a single frame of data. This is useful when using DCAM_ATTACHBUFFER."""
        return False

    def dcam_allocframe(self, h: Handle, framecount: c_int32) -> bool:
        """Allocates the proper amount of memory for a data buffer depending on the number of frames requested and changes the camera status from STABLE to READY. Capturing does not start at this time. This function will fail if called while camera is not in STABLE state."""
        self.arr = np.zeros((framecount.value * 128, 4096), dtype=np.uint16)
        self.ready = 0
        self.fc = framecount.value

        return True

    def dcam_getframecount(self, h: Handle, pFrame: pointer[c_int32]) -> bool:
        """Returns the number of frames allocated in memory by either DCAM_ALLOCFRAME or by DCAM_ATTACHBUFFER. This function will fail is no frames have been allocated."""
        pFrame.contents.value = self.fc
        return True

    def dcam_capture(self, h: Handle) -> bool:
        """This starts capturing images. Camera status must be READY before using this function. If the camera is in SEQUENCE mode, the camera will capture images repeatedly. If the camera is in SNAP mode, the camera will capture only the number of images for frames that were allocated."""
        return True

    def dcam_idle(self, h: Handle) -> bool:
        """This function will stop the capturing of images. If the camera is in BUSY state, it will set it to READY state."""
        return True

    def dcam_wait(
        self,
        h: Handle,
        pCode: pointer[c_int32],
        timeout: c_uint32,
        abortsignal: Handle,
    ) -> bool:
        return False

    def dcam_getstatus(self, h: Handle, pStatus: pointer[c_int32]) -> bool:
        """This returns the state of the current camera operation."""
        pStatus.contents.value = 3
        return True

    def dcam_gettransferinfo(
        self,
        h: Handle,
        pNewestFrameIndex: pointer[c_int32],
        pFrameCount: pointer[c_int32],
    ) -> bool:
        pNewestFrameIndex.contents.value = self.ready
        pFrameCount.contents.value = self.fc
        return True

    def dcam_freeframe(self, h: Handle) -> bool:
        """This frees up the memory allocated from DCAM_ALLOCFRAME. Also sets the status of the camera from READY state to STABLE state. This will fail if the camera is in BUSY state when called."""
        self.fc = 0
        self.ready = 0
        return True

    # /*** --- user memory support --- ***/
    def dcam_attachbuffer(self, h: Handle, frames: pointer[c_void_p], size: c_uint32) -> bool:
        """This allows the user to attach his/her own data buffer instead of using DCAM_ALLOCFRAME and using the DCAM buffer. This function accepts an array of pointers to image buffers. If used, this will take the place of DCAM_ALLOCFRAME and set the camera from STABLE to READY state."""
        return False

    def dcam_releasebuffer(self, h: Handle) -> bool:
        """This function works similar to DCAM_FREEFRAME except that this is used when using DCAM_ATTACHBUFFER. This will set the camera from READY to STABLE state."""
        return False

    # /*** --- data transfer --- ***/
    def dcam_lockdata(
        self,
        h: Handle,
        pTop: pointer[c_void_p],
        pRowbytes: pointer[c_int32],
        frame: c_int32,
    ) -> bool:
        """This locks a frame in the data buffer that will be accessed by the user. When a frame is locked, the capture thread will not write to it. Calling this function will also unlock any existing locked frames. If you set the frame input as -1, you will lock the most recently received frame. Put the frame data address into pTop."""
        if frame.value < self.ready:
            pTop.contents.value = self.arr.ctypes.data
            return True
        return False

    def dcam_lockbits(
        self,
        h: Handle,
        pTop: pointer[c_ubyte],
        pRowbytes: pointer[c_int32],
        frame: c_int32,
    ) -> bool:
        """This works similar to DCAM_LOCKDATA except that the buffer data has been altered for display. For example, 16 bit images are converted to 8 bit images and flipped for easy use in Windows API functions. If you set the frame input as -1, you will lock the most recently received frame."""
        return False

    def dcam_unlockdata(self, h: Handle) -> bool:
        """If a framed has been locked by DCAM_LOCKDATA, this function will unlock it."""
        return True

    def dcam_unlockbits(self, h: Handle) -> bool:
        """If a framed has been locked by DCAM_LOCKBITS, this function will unlock it."""
        return False

    # /*** --- LUT --- ***/
    def dcam_setbitsinputlutrange(self, h: Handle, inMax: c_int32, inMin: c_int32 = DCAM_DEFAULT_ARG) -> bool:
        return False

    def dcam_setbitsoutputlutrange(
        self, h: Handle, outMax: c_ubyte, outMin: c_int32 = DCAM_DEFAULT_ARG
    ) -> bool:
        return False

    # /*** --- extended --- ***/
    def dcam_extended(self, h: Handle, iCmd: c_uint32, param: c_void_p, size: pointer[c_uint32]) -> bool:
        return False

    # /*** --- software trigger --- ***/
    def dcam_firetrigger(self, h: Handle) -> bool:
        return False

    def dcam_getpropertyattr(self, h: Handle, param: pointer[DCAM_PARAM_PROPERTYATTR]) -> bool:
        return False

    def dcam_getpropertyvalue(self, h: Handle, iProp: c_int32, pValue: pointer[c_double]) -> bool:
        return False

    def dcam_setpropertyvalue(self, h: Handle, iProp: c_int32, fValue: c_double) -> bool:
        return False

    def dcam_setgetpropertyvalue(
        self,
        h: Handle,
        iProp: c_int32,
        pValue: pointer[c_double],
        option: c_int32 = DCAM_DEFAULT_ARG,
    ) -> bool:
        return False

    def dcam_querypropertyvalue(
        self,
        h: Handle,
        iProp: c_int32,
        pValue: pointer[c_double],
        option: c_int32 = DCAM_DEFAULT_ARG,
    ) -> bool:
        return False

    def dcam_getnextpropertyid(
        self, h: Handle, pProp: pointer[c_int32], option: c_int32 = DCAM_DEFAULT_ARG
    ) -> bool:
        return False

    def dcam_getpropertyname(
        self, h: Handle, iProp: c_int32, text: Array[c_char], textbytes: c_int32
    ) -> bool:
        return False

    def dcam_getpropertyvaluetext(self, h: Handle, param: pointer[DCAM_PARAM_PROPERTYVALUETEXT]) -> bool:
        return False

    def return_false(self):
        return False
