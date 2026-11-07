r"""Test 4051 -- gen #37 route #315 (expected FAIL): `S(xs)` where `S(B)` has no `__init__` and `B.__init__` stores `a[0]`; PROVED `xs[0] == 0` (CPython 1). REFUSED through the base.
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

class B:
    def __init__(self, a: List[int]) -> None:
        a[0] = a[0] + 1
        self.n = 0

class S(B):
    pass

#@ ensures \result == 0
def f() -> int:
    xs = [0]
    k = S(xs)
    return xs[0]

if __name__ == "__main__":
    assert f() == 0, f()
