#%%
from __future__ import annotations

from collections import defaultdict

from pydantic import BaseModel, validator

from pyseq2.flowcell import Seconds, μLpermin


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
CompiledReagents = dict[str, list[Reagent]]  # Key is group name.


def compile_reagents(reagents: Reagents) -> CompiledReagents:
    reagent_groups: defaultdict[str, list[Reagent]] = defaultdict(list)
    curr_group = ""
    i = 0
    for v in reagents.values():
        if not isinstance(v, ReagentGroup):
            reagent_groups[curr_group].append(v)
            if not curr_group:
                reagent_groups[""].append(v)
            i += 1
            continue

        if i == 0:
            raise ValueError(f"Group {curr_group} has no member.")
        curr_group = v.name
        i = 0

    if i == 0:
        raise ValueError(f"Group {curr_group} has no member.")

    return dict(reagent_groups)
