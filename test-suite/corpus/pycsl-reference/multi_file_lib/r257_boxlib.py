"""r257_boxlib — a class with a `@contextmanager` METHOD that writes `self.n`, imported by the
route #257 witness 2562.
"""
from contextlib import contextmanager
from typing import Iterator


class Box:
    #@ ensures self.n == 0
    def __init__(self) -> None:
        self.n: int = 0

    #@ ensures self.n == \old(self.n) + 1
    #@ assigns self.n
    @contextmanager
    def bump(self) -> Iterator[int]:
        self.n = self.n + 1
        yield 0
