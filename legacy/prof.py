DUMMY = False
import sys

sys.path.append("c:\\Users\\sbsuser\\Desktop\\goff-rotation")

import builtins

from rich import print
from rich.console import Console
from rich.logging import RichHandler

from friendly_hiseq import Components

builtins.__dict__.get("profile", lambda f: f)

print("[green]Holding breath...")

if not DUMMY:
    from friendly_hiseq import FriendlyHiSeq
else:
    from dummy import FriendlyHiSeq  # type: ignore

import logging

from ui import init_ui

logging.basicConfig(
    level="NOTSET",
    format="[yellow]%(name)-10s[/] %(message)s",
    datefmt="[%X]",
    handlers=[RichHandler(rich_tracebacks=True, markup=True)],
)

log = logging.getLogger("rich")
console = Console()
ports = {
    "xstage": "COM9",
    "ystage": "COM10",
    "pumpa": "COM19",
    "pumpb": "COM22",
    "valvea24": "COM20",
    "valvea10": "COM18",
    "valveb24": "COM23",
    "valveb10": "COM21",
    "fpgacommand": "COM11",
    "fpgaresponse": "COM13",
    "laser1": "COM14",
    "laser2": "COM17",
    "arm9chem": "COM8",
}

hs = FriendlyHiSeq(console=console, ports=ports)
from src.instruments.stage import YCmd

hs.y.repl(YCmd.CHECK_POS)
