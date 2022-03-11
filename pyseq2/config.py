from pathlib import Path
from typing import Literal

import yaml
from pydantic import BaseSettings


class Config(BaseSettings):
    machine: Literal["HiSeq2000", "HiSeq2500"] = "HiSeq2000"
    logPath: str = "~/pyseq2/logs"
    logLevel: Literal["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"] = "INFO"


def load_config(path: Path | str = "~/.pyseq/pyseq.yml") -> Config:
    if isinstance(path, str):
        path = Path(path)
    if not path.exists():
        return Config()
    return Config(**yaml.safe_load(path.read_text()))


CONFIG = load_config()
