DUMMY = False

from rich import print
from rich.console import Console
from rich.logging import RichHandler

from friendly_hiseq import Components

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

hs = FriendlyHiSeq(console=console)
init_ui(hs.gen_initialize_seq(skip=[Components.PUMPS, Components.VALVES]))
