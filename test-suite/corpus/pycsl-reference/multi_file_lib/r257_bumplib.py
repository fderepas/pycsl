"""r257_bumplib — a module-level `@contextmanager` FUNCTION that writes its argument's field,
imported by the route #257 witness 2563.
"""
from contextlib import contextmanager
from typing import Iterator


class Box:
    #@ ensures self.n == 0
    def __init__(self) -> None:
        self.n: int = 0


#@ ensures b.n == \old(b.n) + 1
#@ assigns b.n
@contextmanager
def bump(b: Box) -> Iterator[int]:
    b.n = b.n + 1
    yield 0
