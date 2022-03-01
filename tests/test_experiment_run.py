from pyseq2.experiment import Experiment
from pyseq2.experiment.command import Pump
from pyseq2.experiment.reagent import Reagent
from pyseq2.flowcell import FlowCells
from pyseq2.imager import Imager
from pyseq2.utils.ports import get_ports


async def test_run():
    ports = await get_ports()
    imager = await Imager.ainit(ports)
    fcs = await FlowCells.ainit(ports)

    exp = Experiment(
        "test",
        False,
        path=".",
        reagents=[Reagent(name="water", port=14, wait=0.1)],
        cmds=[Pump(reagent="water")],
    )
    await exp.run(fcs, False, imager)
