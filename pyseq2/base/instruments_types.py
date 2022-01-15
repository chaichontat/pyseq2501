"""Instrument types
Was hoping for an exhaustive enum-like syntax but Dict is invariant so no.
At least we have auto-complete for dict keys.
"""

from typing import Callable, Literal, Union, cast

ImagingInstruments = Literal["x", "y", "laser_g", "laser_r"]
FluidicsInstruments = Literal["arm9chem", "arm9pe", "pumpa", "pumpb", "va24", "va10", "vb24", "vb10"]

FPGAInstruments = Literal["optics", "z_obj", "z_tilt"]

# fmt: off
SerialInstruments = ImagingInstruments | FluidicsInstruments | Literal["fpga"]
SerialPorts       = ImagingInstruments | FluidicsInstruments | Literal["fpgacmd", "fpgaresp"]

Instruments = Union[SerialInstruments, FPGAInstruments]

# Pick from ANSI colors.
COLOR = cast(
    dict[SerialInstruments, str],
    dict(
           x="purple",
           y="yellow",
     laser_g="green",
     laser_r="magenta",
    arm9chem="cyan",
      arm9pe="cyan",
        fpga="blue",
    ),
)


FORMATTER = cast(
    dict[SerialInstruments, Callable[[str], str]],
    dict(
           x=lambda x: f"{x}\r",
           y=lambda x: f"1{x}\r\n",  # Axis 1
     laser_g=lambda x: f"{x}\r",
     laser_r=lambda x: f"{x}\r",
    arm9chem=lambda x: f"{x}\r",
      arm9pe=lambda x: f"{x}\r",
        fpga=lambda x: f"{x}\n",
    ),
)
# fmt: on
