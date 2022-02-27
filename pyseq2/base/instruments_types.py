"""Instrument types
Was hoping for an exhaustive enum-like syntax but Dict is invariant so no.
At least we have auto-complete for dict keys.
"""

from typing import Callable, Literal, cast

from pyseq2.utils.utils import λ_str

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
           x=λ_str(lambda x:   f"{x}\r"),
           y=λ_str(lambda x:  f"1{x}\r\n"),  # Axis 1
     laser_g=λ_str(lambda x:   f"{x}\r"),
     laser_r=λ_str(lambda x:   f"{x}\r"),
    arm9chem=λ_str(lambda x:   f"{x}\r"),
      arm9pe=λ_str(lambda x:   f"{x}\r"),
       pumpa=λ_str(lambda x: f"/1{x}\r"),
       pumpb=λ_str(lambda x: f"/1{x}\r"),
    valve_a1=λ_str(lambda x:   f"{x}\r"),
    valve_a2=λ_str(lambda x:   f"{x}\r"),
    valve_b1=λ_str(lambda x:   f"{x}\r"),
    valve_b2=λ_str(lambda x:   f"{x}\r"),
        fpga=λ_str(lambda x:   f"{x}\n"),
    ),
)

SEPARATOR = dict(
           x=b"\r",
           y=b"\r\n",
       pumpa=b"\r\n\xff",
       pumpb=b"\r\n\xff",
    valve_a1=b"\r",
    valve_a2=b"\r",
    valve_b1=b"\r",
    valve_b2=b"\r",
        fpga=b"\r\n",
    )

# fmt: on
