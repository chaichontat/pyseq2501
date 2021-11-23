
class FakeCamera:
    TDI_EXPOSURE_TIME = 0.002568533333333333
    AREA_EXPOSURE_TIME = 0.005025378

    IMG_WIDTH = 4096
    IMG_HEIGHT = 64
    # FRAME_Y =
    IMG_BYTES = 524288

    def __init__(self, id_: Literal[0, 1]) -> None:
        ...

    @contextmanager
    def capture(self) -> Generator[None, None, None]:
        yield

    @contextmanager
    def alloc(self, n_frames: int) -> Generator[None, None, None]:
        yield

    @property
    def status(self) -> Status:
        return Status.Ok

    @property
    def n_frames_taken(self) -> int:
        return int(f_count.value)

    def get_images(self):
        return np.zeros((2048), dtype=np.int16)