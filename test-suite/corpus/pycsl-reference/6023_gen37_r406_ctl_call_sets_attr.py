r"""Test 6023 -- gen #37 route #406 (expected PASS): CONTROL: a `getattr` default over a class whose constructor calls `math.floor` and a file function on `self` (callees the model reads) (CPython 0). PROVED at base and candidate.
"""
# pycsl-expected: PASS
import math


class R:
    def __init__(self) -> None:
        self.x: int = 1
        self.y: int = math.floor(self.x)
        init_more(self)


def init_more(r: R) -> None:
    r.x = 2


#@ ensures \result == 0
def f(r: R) -> int:
    return getattr(r, "k", 0)


if __name__ == "__main__":
    print(f(R()))
