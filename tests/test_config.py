from pathlib import Path

import pyseq2


def test_load_config():
    p = Path("._pyseq.yml")
    p.write_text("machine: HiSeq2500")
    cf = pyseq2.config.load_config((p,))
    assert cf.machine == "HiSeq2500"
    assert cf.ports == tuple(range(1, 25))
    p.unlink()
