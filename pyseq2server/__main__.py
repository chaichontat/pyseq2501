import logging
import os
import webbrowser
from pathlib import Path
from typing import cast

import click
import uvicorn
from asgiref.typing import ASGIApplication
from fastapi.staticfiles import StaticFiles

from .server import gen_server, q_log, q_log2
from .utils.log import setup_web_logger

logger = logging.getLogger(__name__)


@click.command()
@click.option("--port", "-p", type=int, default=8000, help="Port to run the server on (default: 8000).")
@click.option(
    "--host",
    "-h",
    default="localhost",
    help="Hostname to bind to (default: localhost). Set 0.0.0.0 for network access.",
)
@click.option("--open", "-o", help="Open a web browser", is_flag=True)
@click.option("--fake", help="Use fake machine interface.", is_flag=True)
@click.option(
    "--donothost",
    help="Only host the websocket, not the interface. Useful when developing Svelte.",
    is_flag=True,
)
@click.option(
    "--loglevel", type=click.Choice(["debug", "info", "warning", "error", "critical"]), default="info"
)
def run(port: int, host: str, fake: bool, open: bool, donothost: bool, loglevel: str) -> None:
    if os.name == "nt" and fake:
        os.environ["FAKE_HISEQ"] = "1"

    app = gen_server()

    if not donothost:
        try:
            directory = Path(__file__).parent.parent / "build"
            logger.info(f"Looking for interface at {directory}.")
            app.mount("/", StaticFiles(directory=directory, html=True))
        except RuntimeError as e:
            raise RuntimeError(
                "Most likely, the system cannot find the built interface. Run `npm run build` to build."
            ) from e

    setup_web_logger(q_log, q_log2, level=loglevel.upper())

    for _log in ["uvicorn", "uvicorn.access", "uvicorn.error", "fastapi"]:
        logging.getLogger(_log).handlers = logging.getLogger("pyseq2").handlers if _log == "fastapi" else []

    if open:
        webbrowser.open_new_tab(f"http://localhost:{port}/")

    uvicorn.run(cast(ASGIApplication, app), host=host, port=port)


if __name__ == "__main__":
    run()
