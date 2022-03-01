from contextlib import nullcontext

import pytest
import yaml
from hypothesis import given
from hypothesis.strategies import integers
from pydantic import ValidationError

from pyseq2.experiment import Experiment
from pyseq2.experiment.command import Autofocus, Cmd, Goto, Pump, Temp
from pyseq2.experiment.reagent import Reagent, ReagentGroup, Reagents


def test_basic():
    # Flush ports 1, 2, 3 with 250 μL per barrel.
    waters: Reagents = [Reagent(name=f"water{port}", port=port) for port in (1, 2, 3)]
    ops: list[Cmd] = [Pump(reagent=water.name) for water in waters]
    ops.append(Autofocus(channel=0, laser_onoff=True, laser=5, od=0))
    ops.append(Temp(temp=25))

    experiment = Experiment("wash_ports_123", False, path=".", cmds=ops, reagents=waters)
    assert Experiment.parse_raw(experiment.json()) == experiment
    assert Experiment.parse_obj(yaml.safe_load(yaml.dump(experiment.dict()))) == experiment


@given(integers(1, 10))
def test_compile(n: int):
    mix: Reagents = []
    mix.append(Reagent(name="water", port=14))
    mix.append(ReagentGroup(name="gr"))

    cond = n + 1 > 9
    with pytest.raises(ValidationError) if cond else nullcontext():
        mix += (antibodies := [Reagent(name=f"antibody{port}", port=port) for port in range(1, n + 1)])
    if cond:
        return

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
