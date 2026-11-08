r"""Test 4726 -- gen #37 route #351 (expected FAIL): `ys: List[int] = xs` then `ys[0] = 5` (CPython TypeError). VERIFY-FAIL at base, REFUSED now (route #351).
"""
# pycsl-expected: FAIL
from typing import Sequence, List

#@ no_exception \all
#@ requires len(xs) > 0
#@ ensures \result == 5
def f(xs: Sequence[int]) -> int:
    ys: List[int] = xs
    ys[0] = 5
    return ys[0]

if __name__ == "__main__":
    print(f((1, 2)))
