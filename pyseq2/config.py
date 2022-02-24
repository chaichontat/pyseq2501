#%%
from typing import Literal

from pydantic import BaseModel


class Config(BaseModel):
    machine: Literal["HiSeq2000", "HiSeq2500"] = "HiSeq2000"
    logPath: str = "logs"


print(Config.schema_json(indent=2))

# %%
