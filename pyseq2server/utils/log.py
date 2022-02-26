import asyncio
import logging

from pyseq2.utils.log import setup_logger


class AsyncQueueStream:
    def __init__(self, q: asyncio.Queue[str]) -> None:
        self.q = q

    def write(self, __s: str) -> None:
        self.q.put_nowait(__s)


def setup_web_logger(
    q: asyncio.Queue[str] | None = None, *, set_root: bool = True, save: bool = False, level: str = "INFO"
) -> None:

    setup_logger(set_root=set_root, save=save, level=level)
    ps2 = logging.getLogger("pyseq2server")

    if q:
        web_handler = logging.StreamHandler(AsyncQueueStream(q))
        web_handler.setLevel(level)
        web_handler.setFormatter(logging.Formatter("%(message)s"))
        # if set_root:
        logging.getLogger("pyseq2").handlers.append(web_handler)
        ps2.handlers.append(web_handler)

    ps2.setLevel(level)

    for _log in ["uvicorn", "uvicorn.access", "fastapi"]:
        logging.getLogger(_log).handlers = logging.getLogger("pyseq2").handlers if _log == "fastapi" else []
        logging.getLogger(_log).setLevel(level)

    # print(
    #     [
    #         (name, logging.getLogger(name).handlers)
    #         for name in logging.root.manager.loggerDict
    #         if logging.getLogger(name).handlers
    #     ]
    # )
