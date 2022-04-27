import logging
from datetime import datetime
from logging import Formatter, Handler, Logger
from pathlib import Path
from typing import Callable, Coroutine, ParamSpec, TypeVar

from rich.logging import RichHandler
from rich.traceback import install
from rich.console import Console


def setup_logger(*, set_root: bool = False, save: bool = False, level: str = "INFO") -> None:
    """Must be done before any logging is done."""

    install()
    handlers: list[Handler] = [RichHandler(rich_tracebacks=True, markup=True)]
    formatter = Formatter("[yellow]%(name)-10s[/] %(message)s", datefmt="[%H:%M:%S] ")
    handlers[0].setFormatter(formatter)

    if save:
        path = Path(f"./logs/{datetime.now().strftime('%Y%m%d_%H%M%S')}.log")
        path.parent.mkdir(parents=True, exist_ok=True)
        file = open(path, mode='w', encoding='utf-8')
        console = Console(file=file, force_terminal=True)
        handler = RichHandler(rich_tracebacks=True, markup=True, console=console)
        handler.setFormatter(formatter)
        handlers.append(handler)

    if set_root:
        logging.basicConfig(level="CRITICAL", handlers=handlers)

    logger = logging.getLogger("pyseq2")
    logger.setLevel(level)
    logger.handlers = handlers
    logger.propagate = False


P, R = ParamSpec("P"), TypeVar("R")


def init_log(
    logger: Logger, prefix: str | None = None, info: bool = False
) -> Callable[[Callable[P, Coroutine[None, None, R]]], Callable[P, Coroutine[None, None, R]]]:
    def inner(f: Callable[P, Coroutine[None, None, R]]) -> Callable[P, Coroutine[None, None, R]]:
        async def wrapper(*args: P.args, **kwargs: P.kwargs) -> R:
            try:
                name = args[0].name  # type: ignore
            except AttributeError:
                name = type(args[0]).__name__

            if prefix is not None:
                name = f"{prefix} {name}"

            g = logger.info if info else logger.debug
            g(f"Starting {name} initialization.")
            res = await f(*args, **kwargs)
            g(f"Finished {name} initialization.")
            return res

        return wrapper

    return inner
