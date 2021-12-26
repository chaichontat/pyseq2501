# Architecture


## Serial
The HiSeq is controlled by multiple serial ports, with each port typically corresponding to an instrument. Some of the instruments are controlled by the FPGA or the "computer" of the HiSeq, which itself is also controlled by a serial port. All serial ports are connected to the computer through a single USB port.

A single thread, running an asynchronous event loop, serves as a bridge for all serial communications.
This allows concurrent signaling across multiple instruments, dramatically increasing the throughput of the system.
Multiple commands could be sent at once and each incoming message could be processed nearly instantaneously without waiting for the last command to finish.

Communication through the serial port is exceptionally slow (9600 bps or 9600 kHz for each character not including the response time). Therefore, all functions that involve the serial interface or requires any waiting are run in its own thread.
That is, each function should never block the main thread to maintain responsiveness.

### Commands
Commands are strings that are sent through the serial port to each instrument, similar to text messaging.
Some commands evoke a return from an instrument.
Lists of commands are available in the beginning of all instrument files and at `{class}.cmd`.
Commands can be of two formats: `Callable[..., str]` or `str` for commands with and without arguments.

To ensure that there are no silent failures, all responses to commands are compared against the expected response.
Any unexpected response throws an `Exception`. 
The command and its parser are bundled together in the `CmdParse` object.

Sending a `CmdParse` command results in a `Future` object, which could be used to access the parsed response once it is completed.

## Camera

PySeq 2501 communicates with the camera through a DLL file `dcamapi.dll` from Hamamatsu, which probably communicates with the camera through [Camera Link](https://en.wikipedia.org/wiki/Camera_Link).
PySeq 2501 is only guaranteed to work with the original driver version from Illumina. The driver is available upon ReAsOnAbLe ReQuEsT.
I have tried the latest API from Hamamatsu without much success.
The response time is also much better than that over serial communication.

Each camera is individually connected to the frame grabber card.