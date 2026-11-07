r"""Test 4055 -- gen #37 route #315 (expected FAIL): `if d != 1: self.q = 10 // d` under `K(0)`: the ZeroDivisionError was dropped and `\result == 1` PROVED (CPython 0). REFUSED.
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
    def __init__(self, d: int) -> None:
        self.q = 0
        if d != 1:
            self.q = 10 // d

#@ ensures \result == 1
def f() -> int:
    try:
        k = K(0)
    except ZeroDivisionError:
        return 0
    return 1

if __name__ == "__main__":
    assert f() == 1, f()
