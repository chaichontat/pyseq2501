import logging
import os
from typing import cast

import click
import uvicorn
from asgiref.typing import ASGIApplication

from . import app, q_log
from .utils.log import setup_web_logger


@click.command()
@click.option("--fake", help="Use fake machine interface.", is_flag=True)
@click.option("--port", type=int, default=8000, help="Port to run the server on (default: 8000).")
@click.option(
    "--host",
    default="localhost",
    help="Hostname to bind to (default: localhost). Set 0.0.0.0 for network access.",
)
def run(port: int, host: str, fake: bool) -> None:
    setup_web_logger(q_log)
    os.environ["FAKE_HISEQ"] = "1" if fake else "0"

    for _log in ["uvicorn", "uvicorn.access", "uvicorn.error", "fastapi"]:
        logging.getLogger(_log).handlers = logging.getLogger("pyseq2").handlers if _log == "fastapi" else []

    print(
        [
            (name, logging.getLogger(name).handlers)
            for name in logging.root.manager.loggerDict
            if logging.getLogger(name).handlers
        ]
    )
    uvicorn.run(cast(ASGIApplication, app), host=host, port=port)


if __name__ == "__main__":
    run()
