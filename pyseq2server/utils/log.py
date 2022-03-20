import asyncio
import logging

from pyseq2 import setup_logger


class AsyncQueueStream:
    def __init__(self, q: asyncio.Queue[str]) -> None:
        self.q = q

    def write(self, __s: str) -> None:
        self.q.put_nowait(__s)


def setup_web_logger(
    q1: asyncio.Queue[str],
    q2: asyncio.Queue[str],
    *,
    set_root: bool = True,
    save: bool = False,
    level: str = "INFO",
) -> None:

    setup_logger(set_root=set_root, save=save, level=level)

    for _log in ["uvicorn", "uvicorn.access", "uvicorn.error", "fastapi"]:
        logging.getLogger(_log).handlers = logging.getLogger("pyseq2").handlers if _log == "fastapi" else []
        logging.getLogger(_log).setLevel(level)

    ps2 = logging.getLogger("pyseq2")
    ps2e = logging.getLogger("pyseq2.experiment")
    ps2s = logging.getLogger("pyseq2server")

    web_handlers = [logging.StreamHandler(AsyncQueueStream(q)) for q in (q1, q2)]
    for web_handler in web_handlers:
        web_handler.setLevel(level)
        web_handler.setFormatter(logging.Formatter("%(message)s"))
    # if set_root:

    # pyseq2 logs to secondary display.
    ps2.handlers.append(web_handlers[1])
    ps2e.propagate = False

    # pyseq2.experiment logs to primary display.
    ps2e.handlers = [web_handlers[0], ps2.handlers[0]]  # RichHandler

    # pyseq2server logs to primary display.
    ps2s.handlers = [web_handlers[0], ps2.handlers[0]]
    ps2s.setLevel(level)

    # print(
    #     [
    #         (name, logging.getLogger(name).handlers)
    #         for name in logging.root.manager.loggerDict
    #         if logging.getLogger(name).handlers
    #     ]
    # )
