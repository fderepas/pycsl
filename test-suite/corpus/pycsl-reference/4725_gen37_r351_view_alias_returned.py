r"""Test 4725 -- gen #37 route #351 (expected FAIL): `ys = xs; return ys` from `-> List[int]` (CPython TypeError at the later store). VERIFY-FAIL at base, REFUSED now (route #351).
"""
# pycsl-expected: FAIL
from typing import Sequence, List

#@ ensures \result == xs
def as_list(xs: Sequence[int]) -> List[int]:
    ys = xs
    return ys

#@ no_exception \all
#@ requires len(ys) > 0
#@ ensures \result == 5
def poke(ys: List[int]) -> int:
    ys[0] = 5
    return ys[0]

if __name__ == "__main__":
    print(poke(as_list((1, 2))))
