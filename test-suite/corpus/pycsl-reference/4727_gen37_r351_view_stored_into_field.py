r"""Test 4727 -- gen #37 route #351 (expected FAIL): `self.items: List[int] = xs` with `xs: Sequence[int]`, later `b.items[0] = 5` (CPython TypeError). VERIFY-FAIL at base, REFUSED now (route #351).
"""
# pycsl-expected: FAIL
from typing import Sequence, List

class Box:
    def __init__(self, xs: Sequence[int]) -> None:
        self.items: List[int] = xs

#@ no_exception \all
#@ requires len(b.items) > 0
#@ ensures \result == 5
def poke(b: Box) -> int:
    b.items[0] = 5
    return b.items[0]

if __name__ == "__main__":
    print(poke(Box((1, 2))))
