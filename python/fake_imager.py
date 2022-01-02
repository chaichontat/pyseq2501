import numpy as np


class FakeImager:
    @staticmethod
    def take(*args, **kwargs) -> list[np.ndarray]:
        i = np.random.randint(0, 256)
        return 4 * [8 * i * np.ones((256, 256), dtype=np.uint16)]
