DCAM_INIT

This function will initialize DCAM and it will find all supported cameras that are connected to your computer. This will return the number of cameras that were installed. This function must be called before any cameras can be opened.

DCAM_OPEN

This initializes the specified camera determined by the index input. DCAM_INIT will provide the number of cameras available. If successful, it will return a camera handle HDCAM which will be used by other VIs in this library to access the camera. This will also set the camera to UNSTABLE state.

DCAM_CLOSE

Frees all memory used for the camera and releases the handle. Once this function is called, the camera handle will become invalid and cannot be used by other functions. This function will work if the camera is in BUSY state but it is recommended to call this function in STABLE or UNSTABLE state.

DCAM_UNINIT

This function frees all memory and resources used by DCAM. It is recommended that all opened cameras are closed before executing this function. Once this function is called, no more cameras can be opened for use.

DCAM_GETMODELINFO

This is used to get information on a certain camera such as camera type, serial number, and firmware version. DCAM_INIT must be called before this function. This function does not require a camera handle. To select the camera to check, you must supply the index number. Create a constant or control from the String ID terminal to get a list of valid IDs.

DCAM_GETSTRING

This is used to get information on a certain camera such as camera type, serial number, and firmware version. Unlike DCAM_GETMODELINFO this must be used after DCAM_OPEN because this one requires a camera handle. Create a constant or control from the String ID terminal to get a list of valid IDs.

DCAM_GETCAPABILITY

This returns the capabilities of the camera including functions, data types, and bits types. Functions include binning modes, trigger modes, and user memory support. Create a constant or control from the Capability ID terminal to get a list of valid IDs.

DCAM_SETDATATYPE

This function allows you to switch data types if the camera supports multiple data types. Create a constant or control from the Datatype terminal to get a list of data type IDs. However, not all of these IDs are valid for each camera. DCAM_GETCAPABILITY will help you in determining what data types are available for your camera.

DCAM_GETDATATYPE

This returns the value of the current data type. The value returned will be numeric and it may be necessary to use the global variables to process this data.

DCAM_SETBITSTYPE

This sets the display type of the image if the camera supports multiple display types. This is for use with the function DCAM_LOCKBITS. Create a constant or control from the Bitstype terminal to get a list of bits type IDs. However, not all of these IDs are valid for each camera. DCAM_GETCAPABILITY will help you in determining what data types are available for your camera.

DCAM_GETBITSTYPE

This is similar to DCAM_GETDATATYPE. This returns the value of the current bits type. The value returned will be numeric and it may be necessary to use the global variables to process this data.

DCAM_GETDATASIZE

This function returns the dimensions of the data image. For some cameras, the display size and the data size are different.

DCAM_GETBITSSIZE

This function returns the dimensions of the display image. For some cameras, the display size and the data size are different.

DCAM_QUERYUPDATE

Determines if values have been modified since the last time DCAM_QUERYUPDATE has been called and returns the values with the queryflag output. It is important to adjust your application according to these modifications. For example, if you adjust binning settings, the camera may internally adjust other settings such as exposure time. DCAM_QUERYUPDATE will return DCAM_UPDATE_EXPOSURE to let you know that exposure was changed. The value returned will be numeric and it may be necessary to use the global variables to process this data.

DCAM_SETEXPOSURETIME

This allows you to modify the exposure time in seconds of the camera. Depending on the camera, the exposure time that you specify may not be the same exposure time actually set. If necessary, check the actual time set using DCAM_GETEXPOSURETIME.

DCAM_GETEXPOSURETIME

This returns the value of the current exposure time in seconds.

DCAM_SETTRIGGERMODE

This function allows you to switch the current trigger mode. Create a constant or control from the Mode terminal to get a list of trigger mode IDs. However, although they are listed, it may or may not be a valid ID for your camera.

DCAM_GETTRIGGERMODE

This returns the value of the current trigger mode. The value returned will be numeric and it may be necessary to use the global variables to process this data.

DCAM_SETTRIGGERPOLARITY

This will select the polarity of the trigger if the camera has been set to external trigger mode. This function will fail if the camera does not support external trigger. Create a constant or control from the Polarity terminal to get a list of valid IDs.

DCAM_GETTRIGGERPOLARITY

This returns the value of the current polarity. This function will fail if the camera does not support external trigger.

DCAM_SETBINNING

This function will adjust the binning of the camera. Adjusting the binning will also change the output data size, but the pixel depth will remain the same.

DCAM_GETBINNING

This will return the current binning mode of the camera.

DCAM_PRECAPTURE

Sets the capture mode and prepares resources for capturing. This also changes the camera status to STABLE state. Create a constant or control from the Capture Mode terminal to get a list of valid IDs.

DCAM_GETDATARANGE

This function will return the minimum and maximum values possible for the data pixels.

DCAM_GETDATAFRAMEBYTES

This determines the amount of bytes required for a single frame of data. This is useful when using DCAM_ATTACHBUFFER.

DCAM_ALLOCFRAME

Allocates the proper amount of memory for a data buffer depending on the number of frames requested and changes the camera status from STABLE to READY. Capturing does not start at this time. This function will fail if called while camera is not in STABLE state.

DCAM_CAPTURE

This starts capturing images. Camera status must be READY before using this function. If the camera is in SEQUENCE mode, the camera will capture images repeatedly. If the camera is in SNAP mode, the camera will capture only the number of images for frames that were allocated.

DCAM_WAIT

This waits for a user specified event to be generated. Once the event has been signaled, this function will return. Create a constant or control from the Code In terminal to get a list of valid IDs. If the elapsed waiting time exceeds the value set as timeout, then the function will return.

DCAM_IDLE

This function will stop the capturing of images. If the camera is in BUSY state, it will set it to READY state.

DCAM_FREEFRAME

This frees up the memory allocated from DCAM_ALLOCFRAME. Also sets the status of the camera from READY state to STABLE state. This will fail if the camera is in BUSY state when called.

DCAM_GETFRAMECOUNT

Returns the number of frames allocated in memory by either DCAM_ALLOCFRAME or by DCAM_ATTACHBUFFER. This function will fail is no frames have been allocated.

DCAM_GETTRANSFERINFO

Returns the number of frames captured and the index of the most recent captured frame

DCAM_GETSTATUS

This returns the state of the current camera operation.

DCAM_ATTACHBUFFER

This allows the user to attach his/her own data buffer instead of using DCAM_ALLOCFRAME and using the DCAM buffer. This function accepts an array of pointers to image buffers. If used, this will take the place of DCAM_ALLOCFRAME and set the camera from STABLE to READY state.

DCAM_RELEASEBUFFER

This function works similar to DCAM_FREEFRAME except that this is used when using DCAM_ATTACHBUFFER. This will set the camera from READY to STABLE state.

DCAM_LOCKDATA

This locks a frame in the data buffer that will be accessed by the user. When a frame is locked, the capture thread will not write to it. Calling this function will also unlock any existing locked frames. If you set the frame input as -1, you will lock the most recently received frame.

DCAM_UNLOCKDATA

If a framed has been locked by DCAM_LOCKDATA, this function will unlock it.

DCAM_LOCKBITS

This works similar to DCAM_LOCKDATA except that the buffer data has been altered for display. For example, 16 bit images are converted to 8 bit images and flipped for easy use in Windows API functions. If you set the frame input as -1, you will lock the most recently received frame.

DCAM_UNLOCKBITS

If a framed has been locked by DCAM_LOCKBITS, this function will unlock it.

DCAM_FEATUREINQ

This function gives you to ability to dynamically determine specific details of certain features of the camera. These include minimum value, maximum value, stepping value, and default value. Create a constant or control from the Feature terminal to get a list of IDs. However, not all of these IDs may be valid for your camera.

DCAM_FEATURE

This gives you the ability to set many different features of a camera that you cannot control with the basic functions. With this, you also have the ability to get the current value of the feature. Because the camera will sometimes set a different value than you specify, it is best to use the SETGET option on the Direction terminal so the function will return the value of the feature that you just set. Create a constant or control from the Feature terminal to get a list of IDs. However, not all of these IDs may be valid for your camera.

DCAM_SUBARRAYINQ

This determines the sub-array capabilities of the camera at the specified binning mode. This information is necessary to set valid parameters for DCAM_SUBARRAY.

DCAM_SUBARRAY

This function gives you the ability to set a new subarray of the capture. Because setting a new subarray will change the image size, this function should not be called in READY or BUSY state. And this will change the camera state to UNSTABLE. This function also allows you to get the current subarray settings.

DCAM_READOUTTIME

This function will return the current readout time of the camera. This function is not supported by all cameras.

DCAM_SCANMODEINQ

Certain cameras have different scan modes available. Faster speeds allow you to gather more frames while the slower speeds will allow you to get data with less readout noise. Some cameras even have a higher bit depth at the slower speeds. This function will tell you the number of scan speeds available.

DCAM_SCANMODE

Certain cameras have different scan modes available. Faster speeds allow you to gather more frames while the slower speeds will allow you to get data with less readout noise. Some cameras even have a higher bit depth at the slower speeds. This function will allow you to set a new scan speed and/or determine the current scan mode of the camera.

DCAM_SETBITSINPUTLUTRANGE

This sets up a lookup table for the display image. This function only affects the image created using DCAM_LOCKBITS.

DCAM_SETBITSOUTPUTLUTRANGE

This sets up a lookup table for the display image. This function only affects the image created using DCAM_LOCKBITS.
