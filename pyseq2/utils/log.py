import logging
from datetime import datetime
from logging import FileHandler, Formatter, Handler
from pathlib import Path

from rich.logging import RichHandler
from rich.traceback import install


def setup_logger(*, set_root: bool = False, save: bool = False, level: str = "INFO") -> None:
    """Must be done before any logging is done."""

    install()
    handlers: list[Handler] = [RichHandler(rich_tracebacks=True, markup=True)]
    handlers[0].setFormatter(Formatter("[yellow]%(module)-10s[/] %(message)s", datefmt="[%H:%M:%S] "))

    if save:
        path = Path(f"./logs/{datetime.now().strftime('%Y%m%d_%H%M%S')}.log")
        path.parent.mkdir(parents=True, exist_ok=True)
        handlers.append(FileHandler(path))

    if set_root:
        logging.basicConfig(level="CRITICAL", datefmt="[%X]", handlers=handlers)

    logger = logging.getLogger("pyseq2")
    logger.setLevel(level)
    logger.handlers = handlers
