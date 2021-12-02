# Architecture


## Serial
Each file corresponds to an instrument controlled by a serial port. The FPGA or the "computer" of the HiSeq controls more instruments directly.
This is presumably due to instrument interfaces and lower latency requirements.
A single thread, running an asynchronous event loop, serves as a bridge for all serial communications.
This allows concurrent signaling across multiple instruments, dramatically increasing the throughput of the system.
Multiple commands could be sent at once and each incoming message could be processed nearly instantaneously without waiting for the last command to finish.

### Commands
Lists of commands are available in the beginning of all files. Commands can be of two formats: `Callable[..., str]` or `str` for commands with and without arguments.
For commands that elicit a response from an instrument, bundling a command with a parser using `CmdParse` is highly recommended.
Sending a `CmdParse` command results in a `Future` object, which could be used to access the parsed response once it is completed.
Any responses that could not be accounted for using a `CmdParse` object would trigger a warning as these often indicate deviations from a typical behavior.

Since commands are sent without waiting for the previous one to return, a deluge of commands could overwhelm an instrument.
In this case, use the `min_spacing` keyword argument to specify the minimum temporal spacing between commands, defaults to 0.1 seconds.


## Camera

PySeq 2501 communicates with the camera through a DLL file `dcamapi.dll` from Hamamatsu, which probably communicates with the camera through [Camera Link](https://en.wikipedia.org/wiki/Camera_Link).
PySeq 2501 is only guaranteed to work with the original driver version from Illumina.
I have tried the latest API from Hamamatsu without much success.
The response time is also much better than that over serial communication.
