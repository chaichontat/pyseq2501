from __future__ import annotations

import time
from typing import Callable

from pyseq import HiSeq


class FriendlyHiSeq(HiSeq):
    def __init__(self) -> None:
        super().__init__()

    def gen_initialize_seq(self) -> dict[str, Callable[[], None]]:
        def fpga() -> None:
            self.f.initialize()
            self.f.LED(1, "green")
            self.f.LED(2, "green")

        def xy_stage() -> None:
            self.y.command("OFF")
            homed = self.x.initialize()
            self.y.initialize()

        def lasers() -> None:
            self.lasers["green"].initialize()
            self.lasers["red"].initialize()

        def pumps() -> None:
            self.p["A"].initialize()
            self.p["B"].initialize()

        def valves() -> None:
            self.v10["A"].initialize()
            self.v10["B"].initialize()
            self.v24["A"].initialize()
            self.v24["B"].initialize()

        def sync_tdi() -> None:
            while not self.y.check_position():
                time.sleep(1)
            self.y.position = self.y.read_position()
            self.f.write_position(0)

        return {
            "Initalize cameras": lambda: self.initializeCams(),
            "Initialize FPGA": fpga,
            "Initialize xy-stage": xy_stage,
            "Initialize lasers": lasers,
            "Initialize pumps": pumps,
            "Initialize valves": valves,
            "Initialize z-stage": lambda: self.z.initialize(),
            "Initialize objective": lambda: self.obj.initialize(),
            "Initialize optics": lambda: self.optics.initialize(),
            "Initialize temperature control": lambda: self.T.initialize(),
            "Sync TDI encoder with y-stage": sync_tdi,
        }
