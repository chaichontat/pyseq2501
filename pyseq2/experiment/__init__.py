#%%
from __future__ import annotations

from copy import deepcopy
from itertools import pairwise
from logging import getLogger

from pathlib import Path
from typing import Any, Callable


import yaml
from pydantic import BaseModel, root_validator, validator

from .command import *
from .reagent import *

logger = getLogger(__name__)


class Experiment(BaseModel):
    name: str
    path: str
    fc: bool
    reagents: Reagents
    cmds: list[
        Annotated[Pump | Prime | Temp | Hold | Autofocus | TakeImage | Goto, Field(discriminator="op")]
    ]

    """Only allow Reagent in Pump, Prime to be str here.
    Need to use list because JSON does not know how to deal with tuples.
    """

    def __init__(
        self,
        name: str,
        fc: bool,
        *,
        path: str,
        reagents: Reagents,
        cmds: list[Cmd],
    ) -> None:
        # This is here to allow the first two arguments to be positional.
        super().__init__(name=name, fc=fc, path=path, reagents=reagents, cmds=cmds)

    @validator("name")
    def validate_name(cls, name: str) -> str:
        assert name and (all(c for c in name if c.isalpha() or c.isdigit() or c == " "))
        return name

    @validator("path")
    def validate_path(cls, path: str) -> str:
        p = Path(path)
        assert p.is_dir()
        # p.mkdir(exist_ok=True)
        return p.as_posix()

    @validator("fc")
    def validate_fc(cls, fc: int):
        assert fc == 0 or fc == 1
        return fc

    @validator("cmds")
    def validate_cmds(cls, cmds: list[Cmd]) -> list[Cmd]:
        assert len(cmds) > 0, "Commands cannot be empty."
        return cmds

    @validator("reagents")
    def validate_reagents(cls, rs: Reagents) -> Reagents:
        rs_name = [r.name for r in rs]
        ports = [r.port for r in rs if isinstance(r, Reagent)]

        if len(rs_name) != len(set(rs_name)):
            raise ValueError("Reagent name not unique.")

        if len(ports) != len(set(ports)):
            raise ValueError("Ports not unique.")
        assert all(p in range(1, 20) and p != 9 for p in ports), "Invalid port number."

        if isinstance(rs[-1], ReagentGroup):
            raise ValueError("Last item cannot be a group.")

        types = [type(r).__name__ for r in rs]
        for a, b in pairwise(types):
            if a == b == "ReagentGroup":
                raise ValueError("ReagentGroup cannot be stacked.")
        return list(rs)

    @root_validator
    def validate_combi(cls, values: dict[str, Any]) -> dict[str, Any]:
        cmds: list[Cmd] = values["cmds"]
        reagents: Reagents = values["reagents"]
        reagents_name = [r.name for r in reagents]

        for cmd in cmds:
            if isinstance(cmd, Pump | Prime):
                if not isinstance(r := cmd.reagent, str):
                    raise ValueError(f"Reagent in Experiment must be str.")
                if r not in reagents_name:
                    raise ValueError(f"Unknown reagent {r} at {cmd} not in reagent manifest.")

        cpiled_r = compile_reagents(reagents)
        for i, c in enumerate(cmds):
            if isinstance(c, Goto):
                for step in list(cmds[c.step : i]):
                    if isinstance(step, Goto):
                        raise ValueError("Cannot have nested gotos.")
                    if isinstance(step, Pump | Prime) and step.reagent in cpiled_r.groups:
                        assert isinstance(step.reagent, str)
                        if c.n + 1 > len(cpiled_r.groups[step.reagent]):
                            raise ValueError("Number of gotos larger than number of reagents in a group.")

        return values

    def _compile_cmds(self, cpiled_r: CompiledReagents) -> list[Cmd]:
        cmds = deepcopy(self.cmds)
        out: list[Cmd] = []

        # Get rid of Gotos.
        for i, c in enumerate(cmds):
            if isinstance(c, Pump | Prime):  # Replace reagent name with actual.
                assert isinstance(r := c.reagent, str)
                if not r in cpiled_r.groups:
                    c.reagent = cpiled_r.lone[r]

            if isinstance(c, Goto):
                for _ in range(c.n):
                    out += list(deepcopy(cmds[c.step : i]))  # Can't multiply, need deepcopy.
                loop_size = i - c.step

                for j, step in enumerate(out[-loop_size * (c.n + 1) :]):
                    if isinstance(step, Pump | Prime) and isinstance(r := step.reagent, str):
                        step.reagent = cpiled_r.groups[r][j // loop_size]
            else:
                out.append(c)

        for i, c in enumerate(out):  # Verify full replacement
            if isinstance(c, Pump | Prime):
                assert isinstance(c.reagent, Reagent)

        return out

    def compile(self) -> list[Cmd] | str:
        return self._compile_cmds(compile_reagents(self.reagents))

    @staticmethod
    def gen_log(fc: bool, n_steps: int) -> Callable[[int, str], str]:
        def inner(step: int, msg: str) -> str:
            return f"Flowcell {int(fc)} Step {step}/{n_steps}: {msg}"

        return inner

    async def run(
        self,
        fcs: FlowCells,
        i: bool,
        imager: Imager,
        event_queue: asyncio.Queue[Any] | None = None,
        stop_on_exception: bool = True,
    ) -> None | str:

        if isinstance(compiled := self.compile(), str):
            return compiled

        g = self.gen_log(i, len(compiled))
        for step, c in enumerate(compiled):
            try:
                logger.info(g(step, f"{c.op.capitalize()} started."))
                await c.run(fcs, i, imager)
                logger.info(g(step, f"{c.op.capitalize()} finished."))
            except BaseException as e:
                logger.error(g(step, f"{c.op.capitalize()} {type(e).__name__}: {e}."))
                if stop_on_exception:
                    logger.critical("Stopping.")
                    break


#%%
if __name__ == "__main__":
    # Flush ports 1, 2, 3 with 250 μL per barrel simultaneously.
    def test_basic():
        waters: Reagents = [Reagent(name=f"water{port}", port=port) for port in (1, 2, 3)]
        ops: list[Cmd] = [Pump(reagent=water.name) for water in waters]
        ops.append(Autofocus(channel=0, laser_onoff=True, laser=5, od=0))
        ops.append(Temp(temp=25))

        experiment = Experiment("wash_ports_123", False, path=".", cmds=ops, reagents=waters)
        assert Experiment.parse_raw(experiment.json()) == experiment
        assert Experiment.parse_obj(yaml.safe_load(yaml.dump(experiment.dict()))) == experiment

    def test_compile():
        n = 3
        mix: Reagents = []
        mix.append(Reagent(name="water", port=14))
        mix.append(ReagentGroup(name="gr"))
        mix += (antibodies := [Reagent(name=f"antibody{port}", port=port) for port in range(1, n + 1)])

        ops: list[Cmd] = [Pump(reagent="water"), Pump(reagent="gr"), Goto(step=0, n=n - 1)]
        experiment_auto = Experiment("experiment", False, path=".", cmds=ops, reagents=mix)

        ops = []
        for i in range(1, n + 1):
            ops.append(Pump(reagent="water"))
            ops.append(Pump(reagent=f"antibody{i}"))

        w: Reagents = [Reagent(name="water", port=14)]
        w += antibodies
        experiment_man = Experiment(
            "experiment",
            False,
            path=".",
            cmds=ops,
            reagents=w,
        )

        assert experiment_auto.compile() == experiment_man.compile()
        assert Experiment.parse_raw(experiment_auto.json()) == experiment_auto  # Original object not altered.
        assert Experiment.parse_raw(experiment_man.json()) == experiment_man

    test_basic()
    test_compile()
# %%
