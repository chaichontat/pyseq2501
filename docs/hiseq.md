# HiSeq

The system we have is a HiSeq 2000 from 2012. Detailed specifications could be found here.

Basically, it's an epifluorescence microscope with an integrated fluidics system.

Each channel is a Hamamatsu C10000-509 CCD camera with a resolution of `2048 * 128` pixels.

We would typically use the TDI (time delay and integration) mode.
Briefly, we synchronize the speed of the stage and signal collection such that a running charge remains "stationary" with respect to an image point.
This is much better than a typical full "area" shot as we could not take an image when we are moving.

Thinking in terms of the original purpose of the HiSeq reveals much of the engineering decisions.
The system needs to image diffraction-limited points on a 2D plane over distances in the order of centimeters.
By using TDI, we could image an entire vertical slice of a flow cell at high-speed without stitching.
Another issue is $z$-drift. This is dealt with by using 3 separate motors to control the stage height and tilt.
The next problem would be ensuring that two parallel images start and end exactly at the same place.

This is presumably done by using a direct FPGA-camera link that can send "trigger" signals. Details from an analogous model could be found here.
The FPGA can precisely trigger the camera when the $y$ position and $z$ position reaches a certain value.