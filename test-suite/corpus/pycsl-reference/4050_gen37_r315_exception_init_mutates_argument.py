r"""Test 4050 -- gen #37 route #315 (expected FAIL): user exception `E(xs)` whose `__init__` bumps `xs[0]`, raised and caught; `xs[0] == 0` PROVED (CPython 1; #310 residual 4). REFUSED.
"""
# pycsl-expected: FAIL
from typing import List, Dict

#@ requires len(a) >= 1
#@ assigns a[0]
#@ ensures a[0] == \old(a[0]) + 1 and \result == a[0]
def inc(a: List[int]) -> int:
    a[0] = a[0] + 1
    return a[0]

class E(Exception):
    #@ requires len(a) >= 1
    #@ assigns a[0]
    def __init__(self, a: List[int]) -> None:
        a[0] = a[0] + 1
        super().__init__("e")

#@ ensures \result == 0
def f() -> int:
    xs = [0]
    try:
        raise E(xs)
    except E:
        pass
    return xs[0]

if __name__ == "__main__":
    assert f() == 0, f()
