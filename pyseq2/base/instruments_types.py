from typing import Literal, Union

SerialInstruments = Literal["fpga", "laser_r", "laser_g", "x", "y"]
FPGAInstruments = Literal["z", "optics", "objective"]
Instruments = Union[SerialInstruments, FPGAInstruments]
