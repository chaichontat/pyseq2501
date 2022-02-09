from __future__ import annotations

import warnings
from typing import Annotated, Any, Awaitable, Callable, Literal, Optional, Protocol, Sequence

import yaml
from pydantic import BaseModel, Field, root_validator, validator

from pyseq2.flowcell import FlowCells, Seconds, μL, μLpermin
from pyseq2.fluidics.valve import ReagentPorts
from pyseq2.imager import Imager
from pyseq2.utils.utils import until


def default_v_pull() -> μLpermin:
    return 100


class Pumpable(Protocol):
    flowcell: Literal[0, 1]
    port: ReagentPorts
    v_pull: μLpermin = 100
    v_push: μLpermin = 2000


class Waitable(Protocol):
    t: Seconds


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


async def wait(
    flowcells: FlowCells,
    imager: Imager,
    f: Callable[[], Awaitable],
    attempts: int = 120,
    gap: int | float = 1,
) -> None:
    u = 2**5
    await until(f, attempts=attempts, gap=gap)


async def pump(flowcells: FlowCells, imager: Imager, i: Literal[0, 1], r: Reagent, vol: μL):
    await flowcells[i].flow(r.port, vol, v_pull=r.v_pull, v_push=r.v_push, wait=r.wait)


async def prime(flowcells: FlowCells, imager: Imager, i: Literal[0, 1], r: Reagent, vol: μL):
    await flowcells[i].flow(r.port, vol, v_pull=r.v_prime, v_push=r.v_push, wait=r.wait)


async def image(flowcells: FlowCells, imager: Imager, i: Literal[0, 1]):
    ...


class Pump(BaseModel):
    reagent: str
    volume: μL = 250
    op: Literal["pump"] = "pump"


class Prime(BaseModel):
    reagent: str
    volume: μL = 250
    op: Literal["prime"] = "prime"


class Temp(BaseModel):
    temp: int | float
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
    channels: tuple[bool, bool, bool, bool] = (True, True, True, True)
    laser_onoff: tuple[bool, bool] = (True, True)
    lasers: tuple[int, int]
    autofocus: bool = True
    op: Literal["image"] = "image"


class Move(BaseModel):
    xy: tuple[float, float]
    op: Literal["move"] = "move"


Cmd = Annotated[Pump | Prime | Temp | Hold | Autofocus | Image | Move, Field(discriminator="op")]


class Experiment(BaseModel):
    name: str
    flowcell: Literal[0, 1]
    reagents: Sequence[Reagent]
    cmds: Sequence[Cmd]

    def __init__(
        self, name: str, flowcell: Literal[0, 1], *, reagents: Sequence[Reagent], cmds: Sequence[Cmd]
    ) -> None:
        # This is here to allow the first two arguments to be positional.
        super().__init__(name=name, flowcell=flowcell, reagents=reagents, cmds=cmds)

    @root_validator
    def check_reagents(cls, values: dict[str, Any]) -> dict[str, Any]:
        cmds: Sequence[Cmd] = values["cmds"]
        reagents: Sequence[Reagent] = values["reagents"]
        reagents_name = [r.name for r in reagents]

        if len(reagents_name) != len(set(reagents_name)):
            raise ValueError("Reagent name not unique.")

        seen: set[str] = set()
        for cmd in cmds:
            if isinstance(cmd, Pump | Prime):
                if (r := cmd.reagent) not in reagents_name:
                    raise ValueError(f"Unknown reagent {r} at {cmd} not in reagent manifest.")
                seen.add(cmd.reagent)

        if len(reagents_name) > len(seen):
            warnings.warn("Unused reagents found.")

        return values

    @validator("flowcell")
    def fc_check(cls, fc: int):
        assert 0 <= fc <= 1
        return fc


if __name__ == "__main__":
    # Flush ports 1, 2, 3 with 250 μL per barrel simultaneously.
    waters = [Reagent(name=f"water{port}", port=port) for port in (1, 2, 3)]
    ops: list[Cmd] = [Pump(reagent=water.name) for water in waters]
    ops.append(Autofocus())
    ops.append(Temp(temp=25))

    experiment = Experiment("wash_ports_123", 0, cmds=ops, reagents=waters)
    assert Experiment.parse_raw(experiment.json()) == experiment
    assert Experiment.parse_obj(yaml.safe_load(yaml.dump(experiment.dict()))) == experiment
    print(Experiment.parse_obj(yaml.safe_load(yaml.dump(experiment.dict()))))
