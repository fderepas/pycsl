r"""Test 4053 -- gen #37 route #315 (expected FAIL): `self.xs = a; self.xs[0] = 5` mutates the caller list; `ys[0] == 0` PROVED (CPython 5). REFUSED.
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
        self.xs[0] = 5

#@ ensures \result == 0
def f() -> int:
    ys = [0]
    k = K(ys)
    return ys[0]

if __name__ == "__main__":
    assert f() == 0, f()
