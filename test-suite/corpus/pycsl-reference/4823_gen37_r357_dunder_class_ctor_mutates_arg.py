r"""Test 4823 -- gen #37 route #357 (expected FAIL): NEW latent: as 4822 with `self.__class__(ys)`; PROVED (CPython 1). REFUSED (PYCSL-R357-DYNAMIC-CONSTRUCTOR).
"""
# pycsl-expected: FAIL
from typing import List

class W:
    def __init__(self, xs: List[int]) -> None:
        xs.append(1)

    #@ ensures \result == 0
    def m(self, ys: List[int]) -> int:
        n = len(ys)
        o = self.__class__(ys)
        return len(ys) - n


if __name__ == "__main__":
    r = W([]).m([])
    assert r == 1, r
