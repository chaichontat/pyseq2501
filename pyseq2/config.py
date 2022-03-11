from pathlib import Path
from typing import Literal

import yaml
from pydantic import BaseSettings

pyseq_path = Path.home() / Path('.pyseq')

class Config(BaseSettings):
    machine: Literal["HiSeq2000", "HiSeq2500"] = "HiSeq2000"
    logPath: str = str(pyseq_path / 'logs')
    logLevel: Literal["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"] = "INFO"


def load_config(path: Path | str = pyseq_path / 'pyseq.yml') -> Config:
    if isinstance(path, str):
        print("Found path")
        path = Path(path)
        print(path)
    if not path.exists():
        print("Can't find path")
        return Config()
    return Config(**yaml.safe_load(path.read_text()))


CONFIG = load_config()
