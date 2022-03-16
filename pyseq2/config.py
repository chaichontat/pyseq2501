from pathlib import Path
from typing import Literal

import yaml
from pydantic import BaseSettings

pyseq_path = Path.home() / Path(".pyseq")


class Config(BaseSettings):
    machine: Literal["HiSeq2000", "HiSeq2500"] = "HiSeq2000"
    logPath: str = str(pyseq_path / "logs")
    logLevel: Literal["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"] = "INFO"
    enabled_ports: list[int] = [1, 2, 3, 4, 5, 6, 7, 8, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19]
    barrels_per_lane: Literal[1, 2, 4, 8] = 1


def load_config(path: Path | str = pyseq_path / "pyseq.yml") -> Config:
    if isinstance(path, str):
        print("Found path")
        path = Path(path)
        print(path)
    if not path.exists():
        print("Can't find path")
        return Config()
    return Config(**yaml.safe_load(path.read_text()))


CONFIG = load_config()
