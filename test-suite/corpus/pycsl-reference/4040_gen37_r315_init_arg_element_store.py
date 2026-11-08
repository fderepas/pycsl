r"""Test 4040 -- gen #37 route #315 (expected FAIL): `a[0] += 1` in `__init__`; `K(xs)` was a bare record literal and `xs[0] == 0` PROVED (CPython 1). REFUSED: a store to a non-`self` target.
"""
# pycsl-expected: FAIL
from typing import List, Dict

#@ requires len(a) >= 1
#@ assigns a[0]
#@ ensures a[0] == \old(a[0]) + 1 and \result == a[0]
def inc(a: List[int]) -> int:
    a[0] = a[0] + 1
    return a[0]

class K:
    def __init__(self, a: List[int]) -> None:
        a[0] = a[0] + 1
        self.n = 0

#@ ensures \result == 0
def f() -> int:
    xs = [0]
    k = K(xs)
    return xs[0]

if __name__ == "__main__":
    assert f() == 0, f()
