r"""Test 4822 -- gen #37 route #357 (expected FAIL): NEW latent: `o = type(self)(ys)` where `__init__` appends to its argument; `ensures \result == 0` over `len(ys) - n` PROVED (CPython 1: the dynamic constructor's effect was dropped). REFUSED (PYCSL-R357-DYNAMIC-CONSTRUCTOR: a non-literal argument).
"""
# pycsl-expected: FAIL
from typing import List

class W:
    def __init__(self, xs: List[int]) -> None:
        xs.append(1)

    #@ ensures \result == 0
    def m(self, ys: List[int]) -> int:
        n = len(ys)
        o = type(self)(ys)
        return len(ys) - n


if __name__ == "__main__":
    r = W([]).m([])
    assert r == 1, r
