r"""Test 4063 -- gen #37 route #315 (expected FAIL): `self.xs = a; self.xs += [5]` extends the caller list IN PLACE; `len(ys) == 1` PROVED (CPython 2). REFUSED: an augmented store other than `+=`/`-=` of a number.
"""
# pycsl-expected: FAIL
from typing import List, Dict
from dataclasses import dataclass, field, InitVar
from typing import NamedTuple

#@ requires len(a) >= 1
#@ assigns a[0]
#@ ensures a[0] == \old(a[0]) + 1 and \result == a[0]
def inc(a: List[int]) -> int:
    a[0] = a[0] + 1
    return a[0]

class K:
    def __init__(self, a: List[int]) -> None:
        self.xs = a
        self.xs += [5]

#@ ensures \result == 1
def f() -> int:
    ys = [0]
    k = K(ys)
    return len(ys)

if __name__ == "__main__":
    assert f() == 1, f()
