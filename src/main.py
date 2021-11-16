DUMMY = True

if DUMMY:
    from dummy import FriendlyHiSeq
else:
    from friendly_hiseq import FriendlyHiSeq  # type: ignore

import logging

from rich.logging import RichHandler

from ui import init_ui

logging.basicConfig(
    level="NOTSET", format="%(message)s", datefmt="[%X]", handlers=[RichHandler(rich_tracebacks=True)]
)

log = logging.getLogger("rich")

hs = FriendlyHiSeq(logger=log)
init_ui(hs.gen_initialize_seq())
