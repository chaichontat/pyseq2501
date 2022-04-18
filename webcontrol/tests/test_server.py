import contextlib
import threading
import time

import pytest
import uvicorn
from websockets.client import connect

from pyseq2server.routers.status import WebState
from pyseq2server.server import gen_server


# https://github.com/encode/uvicorn/issues/742#issuecomment-674411676
class Server(uvicorn.Server):
    def install_signal_handlers(self):
        pass

    @contextlib.contextmanager
    def run_in_thread(self):
        thread = threading.Thread(target=self.run)
        thread.start()
        try:
            while not self.started:
                time.sleep(1e-3)
            yield
        finally:
            self.should_exit = True
            self.force_exit = True
            thread.join()


@pytest.fixture(scope="session")
def server():
    config = uvicorn.Config(gen_server(), host="127.0.0.1", port=8000)
    with Server(config=config).run_in_thread():
        yield


async def test_ws(server: None) -> None:
    async with connect("ws://localhost:8000/status") as ws:
        assert WebState.parse_raw(await ws.recv())
