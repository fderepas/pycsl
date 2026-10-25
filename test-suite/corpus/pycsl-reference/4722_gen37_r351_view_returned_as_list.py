r"""Test 4722 -- gen #37 route #351 (expected FAIL): `as_list(xs: Sequence[int]) -> List[int]: return xs` PROVED and a verified `poke(ys: List[int])` stored `ys[0] = 5` (CPython `poke(as_list((1, 2)))` TypeError). REFUSED now (PYCSL-SEM-READONLY-VIEW-ESCAPE, route #351).
"""
# pycsl-expected: FAIL
from typing import Sequence, List

#@ ensures \result == xs
def as_list(xs: Sequence[int]) -> List[int]:
    return xs

#@ no_exception \all
#@ requires len(ys) > 0
#@ ensures \result == 5
def poke(ys: List[int]) -> int:
    ys[0] = 5
    return ys[0]

if __name__ == "__main__":
    print(poke(as_list((1, 2))))
