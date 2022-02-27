from typing import Annotated, Literal, Union

from pydantic import BaseModel, Field, ValidationError, root_validator, validator

from pyseq2.flowcell import FlowCells, Seconds, μL, μLpermin


class Reagent(BaseModel):
    name: str
    port: int
    v_pull: μLpermin = 100
    v_prime: μLpermin = 250
    v_push: μLpermin = 2000
    wait: Seconds = 26

    @validator("v_pull", "v_prime", "v_push")
    def v_check(cls, v: μLpermin) -> μLpermin:
        assert 2.5 <= v <= 2000
        return v

    @validator("wait")
    def sec_check(cls, s: Seconds) -> Seconds:
        assert s >= 0
        return s

    @validator("port")
    def port_check(cls, port: int) -> int:
        assert 1 <= port <= 19
        assert port != 9
        return port


class Pump(BaseModel):
    reagent: Reagent | str
    volume: μL = 250
    op: Literal["pump"] = "pump"


class Prime(BaseModel):
    reagent: Reagent | str
    volume: μL = 250
    op: Literal["prime"] = "prime"


class Temp(BaseModel):
    temp: float
    wait: bool = False
    op: Literal["temp"] = "temp"


class Hold(BaseModel):
    time: Seconds
    temp: float
    op: Literal["hold"] = "hold"


class Autofocus(BaseModel):
    op: Literal["autofocus"] = "autofocus"


class Image(BaseModel):
    xy_start: tuple[float, float]
    xy_end: tuple[float, float]
    z_tilt: int
    channels: frozenset[Literal[0, 1, 2, 3]] = frozenset((0, 1, 2, 3))
    lasers: tuple[int, int]
    autofocus: bool = True
    op: Literal["image"] = "image"


Command = Annotated[Pump | Prime | Temp | Hold | Autofocus | Image, Field(discriminator="op")]


class NCmd(BaseModel):
    cmd: Command
    n: int
