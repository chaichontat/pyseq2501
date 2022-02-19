#%%
from __future__ import annotations

from typing import Literal, Sequence

import numpy as np
from pydantic import BaseModel

from fake_imager import FakeImager
from pyseq2.experiment import Experiment
from pyseq2.experiment.command import Cmd, Pump
from pyseq2.experiment.reagent import Reagent, ReagentGroup


class NReagent(BaseModel):
    uid: str | int
    reagent: Reagent | ReagentGroup

    @classmethod
    def default(cls):
        return cls(uid=0, reagent=Reagent.default())


class NCmd(BaseModel):
    uid: str | int
    cmd: Cmd

    @classmethod
    def default(cls) -> NCmd:
        return cls(uid=0, cmd=Pump.default())


class NExperiment(BaseModel):
    name: str
    flowcell: Literal[0, 1]
    reagents: list[NReagent]
    cmds: Sequence[NCmd]

    def to_experiment(self) -> Experiment:
        return Experiment(
            self.name,
            self.flowcell,
            reagents=[r.reagent for r in self.reagents],
            cmds=[c.cmd for c in self.cmds],
        )

    @classmethod
    def default(cls, fc: Literal[0, 1] = 0) -> NExperiment:
        return cls(name="", flowcell=fc, reagents=[NReagent.default()], cmds=[NCmd.default()])
