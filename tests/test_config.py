from pathlib import Path

from pyseq2.config import load_config


def test_load_config():
    p = Path("temp.yml")
    p.write_text("machine: HiSeq2500")
    config = load_config((p,))
    assert config.ports == tuple(range(1, 25))
    p.unlink()
