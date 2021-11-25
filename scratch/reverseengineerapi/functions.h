typedef	unsigned long		_DWORD;
typedef unsigned int	BOOL;

/*** --- parameters --- ***/

BOOL DCAMAPI dcam_queryupdate			( HDCAM h, _DWORD* pFlag, _DWORD reserved DCAM_DEFAULT_ARG );

BOOL DCAMAPI dcam_getbinning			( HDCAM h, int32* pBinning );
BOOL DCAMAPI dcam_getexposuretime		( HDCAM h, double* pSec );
BOOL DCAMAPI dcam_gettriggermode		( HDCAM h, int32* pMode );
BOOL DCAMAPI dcam_gettriggerpolarity	( HDCAM h, int32* pPolarity );

BOOL DCAMAPI dcam_setbinning			( HDCAM h, int32 binning );
BOOL DCAMAPI dcam_setexposuretime		( HDCAM h, double sec );
BOOL DCAMAPI dcam_settriggermode		( HDCAM h, int32 mode );
BOOL DCAMAPI dcam_settriggerpolarity	( HDCAM h, int32 polarity );

/*** --- capturing --- ***/

BOOL DCAMAPI dcam_precapture			( HDCAM h, DCAM_CAPTUREMODE mode );
BOOL DCAMAPI dcam_getdatarange			( HDCAM h, int32* pMax, int32* pMin DCAM_DEFAULT_ARG );
BOOL DCAMAPI dcam_getdataframebytes		( HDCAM h, _DWORD* pSize );

BOOL DCAMAPI dcam_allocframe			( HDCAM h, int32 framecount );
BOOL DCAMAPI dcam_getframecount			( HDCAM h, int32* pFrame );

BOOL DCAMAPI dcam_capture				( HDCAM h );
BOOL DCAMAPI dcam_idle					( HDCAM h );
BOOL DCAMAPI dcam_wait					( HDCAM h, _DWORD* pCode, _DWORD timeout DCAM_DEFAULT_ARG, HDCAMSIGNAL abortsignal DCAM_DEFAULT_ARG );

BOOL DCAMAPI dcam_getstatus				( HDCAM h, _DWORD* pStatus );
BOOL DCAMAPI dcam_gettransferinfo		( HDCAM h, int32* pNewestFrameIndex, int32* pFrameCount );

BOOL DCAMAPI dcam_freeframe				( HDCAM h );

/*** --- user memory support --- ***/

BOOL DCAMAPI dcam_attachbuffer			( HDCAM h, void** frames, _DWORD size );
BOOL DCAMAPI dcam_releasebuffer			( HDCAM h );

/*** --- data transfer --- ***/

BOOL DCAMAPI dcam_lockdata				( HDCAM h, void** pTop, int32* pRowbytes, int32 frame );
BOOL DCAMAPI dcam_lockbits				( HDCAM h, BYTE** pTop, int32* pRowbytes, int32 frame );
BOOL DCAMAPI dcam_unlockdata			( HDCAM h );
BOOL DCAMAPI dcam_unlockbits			( HDCAM h );

/*** --- LUT --- ***/

BOOL DCAMAPI dcam_setbitsinputlutrange	( HDCAM h, int32 inMax, int32 inMin DCAM_DEFAULT_ARG );
BOOL DCAMAPI dcam_setbitsoutputlutrange	( HDCAM h, BYTE outMax, BYTE outMin DCAM_DEFAULT_ARG );

/*** --- Control Panel --- ***/

/* BOOL DCAMAPI dcam_showpanel				( HDCAM h, HWND hWnd, _DWORD reserved DCAM_DEFAULT_ARG ); */

/*** --- extended --- ***/

BOOL DCAMAPI dcam_extended				( HDCAM h, _ui32 iCmd, void* param, _DWORD size );

/*** --- software trigger --- ***/
BOOL DCAMAPI dcam_firetrigger			( HDCAM h );


BOOL DCAMAPI dcam_getpropertyattr	( HDCAM h, DCAM_PROPERTYATTR* param );
BOOL DCAMAPI dcam_getpropertyvalue	( HDCAM h, int32 iProp, double* pValue );
BOOL DCAMAPI dcam_setpropertyvalue	( HDCAM h, int32 iProp, double  fValue );

BOOL DCAMAPI dcam_setgetpropertyvalue(HDCAM h, int32 iProp, double* pValue, int32 option DCAM_DEFAULT_ARG );
BOOL DCAMAPI dcam_querypropertyvalue( HDCAM h, int32 iProp, double* pValue, int32 option DCAM_DEFAULT_ARG );

BOOL DCAMAPI dcam_getnextpropertyid	( HDCAM h, int32* pProp, int32 option DCAM_DEFAULT_ARG );
BOOL DCAMAPI dcam_getpropertyname	( HDCAM h, int32 iProp, char* text, int32 textbytes );
BOOL DCAMAPI dcam_getpropertyvaluetext( HDCAM h, DCAM_PROPERTYVALUETEXT* param );
