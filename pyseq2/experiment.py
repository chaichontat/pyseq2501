#%%
from __future__ import annotations

import math
from collections import defaultdict
from copy import deepcopy
from logging import getLogger
from pathlib import Path
from typing import Annotated, Any, Awaitable, Callable, Literal, Optional, Protocol, Sequence, cast

import numpy as np
import yaml
from pydantic import BaseModel, Field, root_validator, validator

from pyseq2.flowcell import FlowCells, Seconds, _FlowCell, μL, μLpermin
from pyseq2.fluidics.valve import ReagentPorts
from pyseq2.imager import Imager
from pyseq2.utils import coords
from pyseq2.utils.utils import until

logger = getLogger(__name__)


def default_v_pull() -> μLpermin:
    return 100


class Pumpable(Protocol):
    flowcell: Literal[0, 1]
    port: ReagentPorts
    v_pull: μLpermin = 100
    v_push: μLpermin = 2000


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


class ReagentGroup(BaseModel):
    name: str


Reagents = dict[str, Reagent | ReagentGroup]


async def wait(
    flowcells: FlowCells,
    imager: Imager,
    f: Callable[[], Awaitable],
    attempts: int = 120,
    gap: int | float = 1,
) -> None:
    u = 2**5
    await until(f, attempts=attempts, gap=gap)


class Pump(BaseModel):
    reagent: str
    volume: μL = 250
    op: Literal["pump"] = "pump"


async def pump(fc: _FlowCell, cmd: Pump, reagents: Reagents):
    r = reagents[cmd.reagent]
    await fc.flow(r.port, cmd.volume, v_pull=r.v_pull, v_push=r.v_push, wait=r.wait)


class Prime(BaseModel):
    reagent: str
    volume: μL = 250
    op: Literal["prime"] = "prime"


async def prime(fc: _FlowCell, cmd: Prime, reagents: Reagents):
    r = reagents[cmd.reagent]
    await fc.flow(r.port, cmd.volume, v_pull=r.v_prime, v_push=r.v_push, wait=r.wait)


class Temp(BaseModel):
    temp: int | float
    wait: bool = False
    op: Literal["temp"] = "temp"


async def temp(fc: _FlowCell, cmd: Temp):
    await fc.set_temp(cmd.temp)


class Hold(BaseModel):
    time: Seconds
    temp: float
    op: Literal["hold"] = "hold"


class Autofocus(BaseModel):
    op: Literal["autofocus"] = "autofocus"


class TakeImage(BaseModel):
    name: str
    path: str
    xy0: tuple[float, float]
    xy1: tuple[float, float]
    overlap: float
    channels: tuple[bool, bool, bool, bool]
    z_tilt: int | tuple[int, int, int]
    z_obj: int
    laser_onoff: tuple[bool, bool]
    lasers: tuple[int, int]
    flowcell: bool
    od: tuple[float, float]
    z_spacing: int = 0
    z_n: int = 1
    op: Literal["image"] = "image"


async def take_image(imager: Imager, fc: Literal[0, 1], cmd: TakeImage):
    logger.info("Taking images.")
    n_bundles = math.ceil(max(cmd.xy0[1], cmd.xy1[1]) - (min(cmd.xy0[1], cmd.xy1[1])) / 0.048)
    y_start = coords.mm_to_raw(fc, y=min(cmd.xy0[1], cmd.xy1[1]))

    x_step = cmd.overlap * 0.768
    x_n = math.ceil((max(cmd.xy0[0], cmd.xy1[0]) - (x_start := min(cmd.xy0[0], cmd.xy1[0]))) / x_step)

    xs = [coords.mm_to_raw(fc, x=x_start + n * x_step) for n in range(x_n)]
    zs = [cmd.z_obj + n * cmd.z_spacing for n in range(cmd.z_n)]

    channels = cast(frozenset[Literal[0, 1, 2, 3]], frozenset(i for i, c in enumerate(cmd.channels) if c))

    # Test if we can write to the directory
    path = Path(cmd.path) / cmd.name
    paths = [path.parent / f"{path.stem}_{i}.tif" for i in range(len(xs))]
    [p.touch() for p in paths]

    big_img = np.empty((len(zs), len(channels), 128 * n_bundles), dtype=np.uint16)
    for p, x in zip(paths, xs):
        for idx, z in enumerate(zs):
            await imager.move(x=x, y=y_start, z_obj=z, z_tilt=cmd.z_tilt)
            img, state = await imager.take(n_bundles, channels=channels)
            big_img[idx] = img
        imager.save(p, big_img)  # TODO state per each stack.

    logger.info("Done taking images.")


class Move(BaseModel):
    xy: tuple[float, float]
    op: Literal["move"] = "move"


# async def move(imager: Imager, i: Literal[0,1]):


class Goto(BaseModel):
    step: int
    n: int
    op: Literal["goto"] = "goto"


Cmd = Annotated[Pump | Prime | Temp | Hold | Autofocus | TakeImage | Move | Goto, Field(discriminator="op")]


class Experiment(BaseModel):
    name: str
    flowcell: Literal[0, 1]
    reagents: dict[str, Reagent | ReagentGroup]
    cmds: Sequence[Cmd]

    def __init__(
        self,
        name: str,
        flowcell: Literal[0, 1],
        *,
        reagents: dict[str, Reagent | ReagentGroup],
        cmds: Sequence[Cmd],
    ) -> None:
        # This is here to allow the first two arguments to be positional.
        super().__init__(name=name, flowcell=flowcell, reagents=reagents, cmds=cmds)

    @root_validator
    def check_reagents(cls, values: dict[str, Any]) -> dict[str, Any]:
        cmds: Sequence[Cmd] = values["cmds"]
        reagents: Reagents = values["reagents"]
        reagents_name = [r for r in reagents]

        if len(reagents_name) != len(set(reagents_name)):
            raise ValueError("Reagent name not unique.")

        seen: set[str] = set()
        for cmd in cmds:
            if isinstance(cmd, Pump | Prime):
                if (r := cmd.reagent) not in reagents_name:
                    raise ValueError(f"Unknown reagent {r} at {cmd} not in reagent manifest.")
                seen.add(cmd.reagent)

        # if len(reagents_name) > len(seen):
        #     warnings.warn("Unused reagents found.")

        return values

    @validator("flowcell")
    def fc_check(cls, fc: int):
        assert 0 <= fc <= 1
        return fc

    @validator("reagents")
    def val_reagents(
        cls, v: list[Reagent | ReagentGroup] | dict[str, Reagent | ReagentGroup]
    ) -> dict[str, Reagent | ReagentGroup]:
        if not isinstance(v, dict):
            return {x.name: x for x in v}
        return v

    def _compile_reagents(self) -> dict[str, list[Reagent]]:
        reagent_groups: defaultdict[str, list[Reagent]] = defaultdict(list)
        curr_group = ""
        i = 0
        for v in self.reagents.values():
            if not isinstance(v, ReagentGroup):
                reagent_groups[curr_group].append(v)
                i += 1
                continue

            if i == 0:
                raise ValueError(f"Group {curr_group} has no member.")
            curr_group = v.name
            i = 0

        if i == 0:
            raise ValueError(f"Group {curr_group} has no member.")

        return dict(reagent_groups)

    def _compile_cmds(self, compiled_reagents: dict[str, list[Reagent]]) -> list[Cmd]:
        out: list[Cmd] = []
        # Get rid of Gotos.
        for i, c in enumerate(self.cmds):
            if not isinstance(c, Goto):
                out.append(deepcopy(c))
                continue
            for _ in range(c.n):
                out += deepcopy(self.cmds[c.step : i])

        group_count = {k: 0 for k in compiled_reagents}
        for c in out:
            try:
                if (r := c.reagent) in compiled_reagents:  # type: ignore  # Group name
                    c.reagent = compiled_reagents[r][group_count[r]]  # type: ignore
                    group_count[r] += 1
                else:
                    c.reagent = deepcopy(self.reagents[r])  # type: ignore
            except AttributeError:
                ...
        return out

    def compile(self) -> list[Cmd]:
        return self._compile_cmds(self._compile_reagents())


#%%
if __name__ == "__main__":
    # Flush ports 1, 2, 3 with 250 μL per barrel simultaneously.
    def test_basic():
        waters = {f"water{port}": Reagent(name=f"water{port}", port=port) for port in (1, 2, 3)}
        ops: list[Cmd] = [Pump(reagent=water) for water in waters]
        ops.append(Autofocus())
        ops.append(Temp(temp=25))

        experiment = Experiment("wash_ports_123", 0, cmds=ops, reagents=waters)
        assert Experiment.parse_raw(experiment.json()) == experiment
        assert Experiment.parse_obj(yaml.safe_load(yaml.dump(experiment.dict()))) == experiment

    def test_compile():
        mix = {}
        mix["water"] = Reagent(name="water", port=5)
        mix["gr"] = ReagentGroup(name="gr")
        mix |= (
            antibodies := {
                f"antibody{port}": Reagent(name=f"antibody{port}", port=port) for port in (1, 2, 3)
            }
        )

        ops: list[Cmd] = [Pump(reagent="water"), Pump(reagent="gr"), Goto(step=0, n=2)]
        experiment_auto = Experiment("experiment", 0, cmds=ops, reagents=mix)

        ops = []
        for i in range(1, 4):
            ops.append(Pump(reagent="water"))
            ops.append(Pump(reagent=f"antibody{i}"))

        experiment_man = Experiment(
            "experiment", 0, cmds=ops, reagents={"water": Reagent(name="water", port=5)} | antibodies
        )

        assert experiment_auto.compile() == experiment_man.compile()
        assert Experiment.parse_raw(experiment_auto.json()) == experiment_auto  # Original object not altered.
        assert Experiment.parse_raw(experiment_man.json()) == experiment_man

    test_basic()
    test_compile()
# %%
