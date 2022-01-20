import json
from typing import Literal, Sequence, get_args

import yaml
from pydantic import BaseModel, validator

from pyseq2.flowcell import Seconds, μL, μLpermin


def default_v_pull() -> μLpermin:
    return 100


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


class Command(BaseModel):
    name: Literal["prime", "pump", "flow", "autofocus", "initialize", "image", "temp", "wait"]
    flowcell: int
    reagent: Reagent
    volume: μL = 250

    @validator("flowcell")
    def fc_check(cls, fc: int):
        assert 0 <= fc <= 1
        return fc


class Experiment(BaseModel):
    name: str
    ops: Sequence[Sequence[Command] | Command]  # One level tree for simultaneous events.


if __name__ == "__main__":

    # Flush ports 1, 2, 3 of both flowcells with 250 μL per barrel simultaneously.
    waters = [Reagent(name="water", port=port) for port in (1, 2, 3)]
    ops = [[Command(name="pump", flowcell=i, reagent=water) for i in (0, 1)] for water in waters]

    experiment = Experiment(name="wash_all_ports", ops=ops)
    print(experiment.json())
    print(yaml.dump(experiment.dict()))

    assert Experiment.parse_obj(json.loads(experiment.json())) == experiment
    assert Experiment.parse_obj(yaml.safe_load(yaml.dump(experiment.dict()))) == experiment
