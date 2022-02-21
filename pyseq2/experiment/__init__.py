#%%
from __future__ import annotations

from copy import deepcopy
from logging import getLogger
from typing import Any, Literal, Sequence

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
    cmds: Sequence[Cmd]

    """Only allow Reagent in Pump, Prime to be str here.
    """

    def __init__(
        self,
        name: str,
        fc: bool,
        *,
        path: str,
        reagents: Reagents,
        cmds: Sequence[Cmd],
    ) -> None:
        # This is here to allow the first two arguments to be positional.
        super().__init__(name=name, fc=fc, path=path, reagents=reagents, cmds=cmds)

    @root_validator
    def check_reagents(cls, values: dict[str, Any]) -> dict[str, Any]:
        cmds: Sequence[Cmd] = values["cmds"]
        reagents: Reagents = values["reagents"]
        reagents_name = [r.name for r in reagents]

        if len(reagents_name) != len(set(reagents_name)):
            raise ValueError("Reagent name not unique.")

        # seen: set[str] = set()
        for cmd in cmds:
            if isinstance(cmd, Pump | Prime):
                if (r := cmd.reagent) not in reagents_name:
                    raise ValueError(f"Unknown reagent {r} at {cmd} not in reagent manifest.")
                # seen.add(cmd.reagent)

        # if len(reagents_name) > len(seen):
        #     warnings.warn("Unused reagents found.")
        return values

    @validator("fc")
    def fc_check(cls, fc: int):
        assert 0 <= fc <= 1
        return fc

    @validator("reagents")
    def val_reagents(cls, v: Reagents) -> Reagents:
        # if not isinstance(v, dict):
        #     return {x.name: x for x in v}
        return v

    def _compile_cmds(self, compiled_reagents: CompiledReagents) -> list[Cmd]:
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
                    assert isinstance(r, str)
                    c.reagent = compiled_reagents[r][group_count[r]]  # type: ignore
                    group_count[r] += 1
                else:
                    c.reagent = deepcopy(self.reagents[r])  # type: ignore
            except AttributeError:
                ...
        return out

    def compile(self) -> list[Cmd]:
        return self._compile_cmds(compile_reagents(self.reagents))


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
        mix: Reagents = []
        mix.append(Reagent(name="water", port=5))
        mix.append(ReagentGroup(name="gr"))
        mix += (antibodies := [Reagent(name=f"antibody{port}", port=port) for port in (1, 2, 3)])

        ops: list[Cmd] = [Pump(reagent="water"), Pump(reagent="gr"), Goto(step=0, n=2)]
        experiment_auto = Experiment("experiment", False, path=".", cmds=ops, reagents=mix)

        ops = []
        for i in range(1, 4):
            ops.append(Pump(reagent="water"))
            ops.append(Pump(reagent=f"antibody{i}"))

        experiment_man = Experiment(
            "experiment",
            False,
            path=".",
            cmds=ops,
            reagents=tuple([Reagent(name="water", port=5)] + antibodies),
        )

        assert experiment_auto.compile() == experiment_man.compile()
        assert Experiment.parse_raw(experiment_auto.json()) == experiment_auto  # Original object not altered.
        assert Experiment.parse_raw(experiment_man.json()) == experiment_man

    test_basic()
    test_compile()
# %%
