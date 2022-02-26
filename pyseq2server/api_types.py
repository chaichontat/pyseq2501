from __future__ import annotations

from typing import Literal, Sequence

from pydantic import BaseModel, root_validator

from pyseq2.experiment import Experiment
from pyseq2.experiment.command import *
from pyseq2.experiment.reagent import Reagent, ReagentGroup
from pyseq2.imager import State
from pyseq2.utils.coords import mm_to_raw


class MoveManual(BaseModel):
    xy0: tuple[float, float] | None = None
    xy1: tuple[float, float] | None = None
    z_tilt: int | tuple[int, int, int] | None = None
    z_obj: int | None = None
    laser_onoff: tuple[bool, bool] | None = None
    lasers: tuple[int, int] | None = None
    shutter: bool | None = None
    od: tuple[float, float] | None = None

    @root_validator
    def validate_xy(cls, values: dict[str, Any]) -> dict[str, Any]:
        if not bool(values["xy0"]) ^ bool(values["xy1"]):
            raise ValueError("Either and either xy0 or xy1 must be specified.")
        return values

    def to_state(self) -> State:
        out = self.copy(exclude={"xy0", "xy1"})
        if self.xy0:
            assert self.xy1 is None
            out.x, out.y = mm_to_raw(False, x=self.xy0[0], y=self.xy0[1])
        if self.xy1:
            assert self.xy0 is None
            out.x, out.y = mm_to_raw(True, x=self.xy1[0], y=self.xy1[1])
        return cast(State, out)

    async def run(self, i: Imager) -> None:
        await i.move(**self.to_state().dict())


class CommandResponse(BaseModel):
    step: tuple[int, int, int] | None = None
    msg: str | None = None
    error: str | None = None


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


class NTakeImage(TakeImage):
    fc: bool

    @classmethod
    def default(cls) -> NTakeImage:
        ori = super().default()
        return NTakeImage(**ori.dict(), fc=False)


class UserSettings(BaseModel):
    """None happens when the user left the input empty."""

    block: Literal["", "moving", "ejecting", "capturing", "previewing"]
    max_uid: int
    exps: list[NExperiment]
    image_params: NTakeImage

    @classmethod
    def default(cls) -> UserSettings:
        return UserSettings(
            block="",
            max_uid=2,
            exps=[NExperiment.default(False), NExperiment.default(True)],
            image_params=NTakeImage.default(),
        )
