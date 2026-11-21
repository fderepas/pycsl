r"""Test 4728 -- gen #37 route #351 (expected FAIL): `ys = xs; ys[0] = 5` (CPython TypeError). REFUSED at base by the abstract-subscript-store check, REFUSED now by route #351 first.
"""
# pycsl-expected: FAIL
from typing import Sequence

#@ no_exception \all
#@ requires len(xs) > 0
#@ ensures \result == 5
def f(xs: Sequence[int]) -> int:
    ys = xs
    ys[0] = 5
    return ys[0]

if __name__ == "__main__":
    print(f((1, 2)))
