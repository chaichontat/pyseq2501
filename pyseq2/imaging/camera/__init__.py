from concurrent.futures import ThreadPoolExecutor

from .dcam_api import CheckedDCAMAPI

API = CheckedDCAMAPI()  # type: ignore
EXECUTOR = ThreadPoolExecutor(1)
