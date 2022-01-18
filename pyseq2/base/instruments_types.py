"""Instrument types
Was hoping for an exhaustive enum-like syntax but Dict is invariant so no.
At least we have auto-complete for dict keys.
"""

from typing import Callable, Literal, cast

ImagingInstruments = Literal["x", "y", "laser_g", "laser_r"]
FPGAInstruments = Literal["optics", "z_obj", "z_tilt"]

ValveName = Literal["valve_a1", "valve_a2", "valve_b1", "valve_b2"]
FluidicsInstruments = Literal["arm9chem", "arm9pe", "pumpa", "pumpb"] | ValveName

# fmt: off
SerialInstruments = ImagingInstruments | FluidicsInstruments | Literal["fpga"]
SerialPorts       = ImagingInstruments | FluidicsInstruments | Literal["fpgacmd", "fpgaresp"]

Instruments = SerialInstruments | FPGAInstruments

# https://rich.readthedocs.io/en/stable/appendix/colors.html?highlight=color#standard-colors
COLOR = cast(
    dict[SerialInstruments, str],
    dict(
           x="purple",
           y="yellow",
     laser_g="bright_green",
     laser_r="magenta",
    arm9chem="cyan1",
      arm9pe="grey35",
       pumpa="bright_cyan",
       pumpb="bright_cyan",
    valve_a1="royal_blue1",
    valve_a2="royal_blue1",
    valve_b1="royal_blue1",
    valve_b2="royal_blue1",
        fpga="blue",
    ),
)


FORMATTER = cast(
    dict[SerialInstruments, Callable[[str], str]],
    dict(
           x=lambda x:   f"{x}\r",
           y=lambda x:  f"1{x}\r\n",  # Axis 1
     laser_g=lambda x:   f"{x}\r",
     laser_r=lambda x:   f"{x}\r",
    arm9chem=lambda x:   f"{x}\r",
      arm9pe=lambda x:   f"{x}\r",
       pumpa=lambda x: f"/1{x}\r",
       pumpb=lambda x: f"/1{x}\r",
    valve_a1=lambda x:   f"{x}\r",
    valve_a2=lambda x:   f"{x}\r",
    valve_b1=lambda x:   f"{x}\r",
    valve_b2=lambda x:   f"{x}\r",
        fpga=lambda x:   f"{x}\n",
    ),
)
# fmt: on
