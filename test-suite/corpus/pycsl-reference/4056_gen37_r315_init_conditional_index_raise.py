r"""Test 4056 -- gen #37 route #315 (expected FAIL): `if b: self.n = a[0]` under `K([], True)`: the IndexError was dropped and `\result == 1` PROVED (CPython 0). REFUSED.
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
    def __init__(self, a: List[int], b: bool) -> None:
        self.n = 0
        if b:
            self.n = a[0]

#@ ensures \result == 1
def f() -> int:
    try:
        k = K([], True)
    except IndexError:
        return 0
    return 1

if __name__ == "__main__":
    assert f() == 1, f()
