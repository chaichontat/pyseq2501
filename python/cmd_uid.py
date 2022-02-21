#%%
from __future__ import annotations

from typing import Literal, Sequence

from pydantic import BaseModel

from pyseq2.experiment import Experiment
from pyseq2.experiment.command import *
from pyseq2.experiment.reagent import Reagent, ReagentGroup


class NReagent(BaseModel):
    uid: str | int
    reagent: Reagent | ReagentGroup

    @classmethod
    def default(cls):
        return cls(uid=0, reagent=Reagent.default())


class NCmd(BaseModel):
    uid: str | int
    cmd: Annotated[Pump | Prime | Temp | Hold | Autofocus | TakeImage | Goto, Field(discriminator="op")]

    @classmethod
    def default(cls) -> NCmd:
        return cls(uid=0, cmd=Pump.default())


class NExperiment(BaseModel):
    name: str
    path: str
    fc: bool
    reagents: Sequence[NReagent]
    cmds: Sequence[NCmd]

    def to_experiment(self) -> Experiment:
        return Experiment(
            self.name,
            self.fc,
            path=self.path,
            reagents=[r.reagent for r in self.reagents],
            cmds=[c.cmd for c in self.cmds],
        )

    @classmethod
    def from_experiment(cls, e: Experiment, uid: int) -> NExperiment:
        reagents = [NReagent(uid=i + uid, reagent=r) for i, r in enumerate(e.reagents, 1)]
        uid += len(e.reagents)
        cmds = [NCmd(uid=uid + i, cmd=c) for i, c in enumerate(e.cmds, 1)]

        return NExperiment(name=e.name, path=e.path, fc=e.fc, reagents=reagents, cmds=cmds)

    @classmethod
    def default(cls, fc: bool = False) -> NExperiment:
        return cls(name="", path=".", fc=fc, reagents=[NReagent.default()], cmds=[NCmd.default()])
