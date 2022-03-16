from pathlib import Path
from typing import Any, Literal

import yaml
from pydantic import BaseSettings, validator

pyseq_path = Path.home() / Path(".pyseq")


class Config(BaseSettings):
    machine: Literal["HiSeq2000", "HiSeq2500"] = "HiSeq2000"
    logPath: str = str(pyseq_path / "logs")
    logLevel: Literal["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"] = "INFO"
    barrels_per_lane: Literal[1, 2, 4, 8] = 1

    enabled_ports: tuple[int, ...] = None  # type: ignore

    # Hack until https://github.com/samuelcolvin/pydantic/pull/2625 is merged.
    @validator("enabled_ports", pre=True, always=True)
    def set_enabled_ports(cls, v: tuple[int, ...], values: dict[str, Any]) -> tuple[int, ...]:
        match values["machine"]:
            case "HiSeq2000":
                return tuple((i for i in range(1, 20) if i != 9))
            case "HiSeq2500":
                return tuple(range(1, 25))
            case _:
                raise ValueError("Invalid machine.")


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
