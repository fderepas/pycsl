r"""Test 4052 -- gen #37 route #315 (expected FAIL): `O.__init__` constructs `K(a)` whose `__init__` calls `inc(a)`; PROVED (CPython 1). REFUSED transitively.
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
        self.n = inc(a)

class O:
    def __init__(self, a: List[int]) -> None:
        self.k = K(a)

#@ ensures \result == 0
def f() -> int:
    xs = [0]
    o = O(xs)
    return xs[0]

if __name__ == "__main__":
    assert f() == 0, f()
