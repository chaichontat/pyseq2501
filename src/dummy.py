from __future__ import annotations

import time
from typing import Callable


class FriendlyHiSeq:
    def __init__(self) -> None:
        super().__init__()

    def gen_initialize_seq(self) -> dict[str, Callable[[], None]]:
        seq = [
            "Initalize cameras",
            "Initialize FPGA",
            "Initialize xy-stage",
            "Initialize lasers",
            "Initialize pumps",
            "Initialize valves",
            "Initialize z-stage",
            "Initialize objective",
            "Initialize optics",
            "Initialize temperature control",
            "Sync TDI encoder with y-stage",
        ]
        return {s: lambda: time.sleep(0.5) for s in seq}
