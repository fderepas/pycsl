r"""Test 4062 -- gen #37 route #315 (expected PASS): CONTROL (expected PASS): `super().__init__(n)` to a modelled base is unaffected.
"""
# pycsl-expected: PASS
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
    def __init__(self, n: int) -> None:
        self.n = n

class S(B):
    def __init__(self, n: int) -> None:
        super().__init__(n)
        self.m = 2

#@ ensures \result == 0
def f() -> int:
    xs = [0]
    s = S(5)
    return xs[0]

if __name__ == "__main__":
    assert f() == 0, f()
