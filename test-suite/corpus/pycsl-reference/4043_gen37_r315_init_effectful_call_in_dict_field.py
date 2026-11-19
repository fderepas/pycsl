r"""Test 4043 -- gen #37 route #315 (expected FAIL): `self.d = {0: inc(a)}`; `xs[0] == 0` PROVED (CPython 1). REFUSED.
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
        self.d = {0: inc(a)}

#@ ensures \result == 0
def f() -> int:
    xs = [0]
    k = K(xs)
    return xs[0]

if __name__ == "__main__":
    assert f() == 0, f()
