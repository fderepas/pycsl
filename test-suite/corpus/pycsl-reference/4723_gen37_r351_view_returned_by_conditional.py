r"""Test 4723 -- gen #37 route #351 (expected FAIL): `return xs if c else xs` from `-> List[int]` PROVED (CPython TypeError at the later store). REFUSED now (route #351).
"""
# pycsl-expected: FAIL
from typing import Sequence, List

#@ ensures \result == xs
def as_list(xs: Sequence[int]) -> List[int]:
    return xs if len(xs) > 0 else xs

#@ no_exception \all
#@ requires len(ys) > 0
#@ ensures \result == 5
def poke(ys: List[int]) -> int:
    ys[0] = 5
    return ys[0]

if __name__ == "__main__":
    print(poke(as_list((1, 2))))
