r"""Test 4059 -- gen #37 route #315 (expected PASS): CONTROL (expected PASS): a field initialiser (`self.xs = a`, `self.n = n + 1`, a conditional store) stays modelled and proves.
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

class K:
    def __init__(self, a: List[int], n: int) -> None:
        self.xs = a
        self.n = n + 1
        self.m = 0
        if n > 3:
            self.m = 1

#@ ensures \result == 3
def f() -> int:
    ys = [0]
    k = K(ys, 2)
    return k.n + ys[0]

if __name__ == "__main__":
    assert f() == 3, f()
