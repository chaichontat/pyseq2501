# PEPrimingPump probably used some non-serial communications method.
# Useless here.

# from __future__ import annotations

# import logging

# from pyseq2.base.instruments import UsesSerial
# from pyseq2.com.async_com import COM, CmdParse
# from pyseq2.utils.utils import chkrng, ok_if_match, ok_re

# logger = logging.getLogger(__name__)


# class PEPortCmd:
#     ID = CmdParse("?IDN", ok_if_match("Illumina,PCIO Controller,0,v0.0035:A1"))
#     VALVE = CmdParse(chkrng(lambda fc, i: f"PVALVE:{fc}:{i}", 0, 1), ok_if_match("A1"))
#     WASTE = CmdParse(chkrng(lambda fc, i: f"WASTE:{fc}:{i}", 0, 1), ok_if_match("A1"))
#     IS_MOVING = CmdParse(
#         chkrng(lambda fc: f"?PMOV:{fc}", 0, 1), ok_re(r"([01]:A1")
#     )  # Guess: fluid is in the port moving.


# class PEPort(UsesSerial):
#     @classmethod
#     async def ainit(cls, port_tx: str) -> PEPort:
#         self = cls()
#         self.com = await COM.ainit("arm9pe", port_tx)
#         return self

#     def __init__(self) -> None:
#         self.com: COM
