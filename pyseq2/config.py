# pyright: reportIncompatibleVariableOverride = false
from logging import getLogger
from pathlib import Path
from typing import Any, Literal

import yaml
from pydantic import BaseSettings, validator

PATH = Path.home() / ".pyseq2"
PATH.mkdir(exist_ok=True)

logger = getLogger(__name__)


class Config(BaseSettings):
    class Config:
        allow_mutation = False

    machine: Literal["HiSeq2000", "HiSeq2500"] = "HiSeq2000"
    logPath: str = (PATH / "logs").as_posix()
    logLevel: Literal["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"] = "INFO"
    barrelsPerLane: Literal[1, 2, 4, 8] = 1
    ports: tuple[int, ...] = None  # type: ignore

    # Hack until https://github.com/samuelcolvin/pydantic/pull/2625 is merged.
    @validator("ports", pre=True, always=True)
    def set_ports(cls, v: tuple[int, ...], values: dict[str, Any]) -> tuple[int, ...]:
        match values["machine"]:
            case "HiSeq2000":
                return tuple(i for i in range(1, 20) if i != 9)
            case "HiSeq2500":
                return tuple(range(1, 25))
            case _:
                raise ValueError("Invalid machine.")


def load_config(paths: tuple[Path | str, ...] = (PATH / "pyseq.yml",)) -> Config:
    for path in paths:
        if isinstance(path, str):
            path = Path(path)
        if not path.exists():
            continue
        return Config(**yaml.safe_load(path.read_text()))

    logger.info("Config file not found. Using defaults.")
    return Config()


CONFIG = load_config()
