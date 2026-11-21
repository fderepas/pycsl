r"""Test 3813 -- gen #37 route #306 (expected FAIL): `max(s, default=bump(xs))`: the lowering DROPS `default`, Python evaluates it; a non-literal `default` is now REFUSED.
"""
# pycsl-expected: FAIL
from typing import List

#@ requires len(a) >= 1
#@ assigns a[0]
#@ ensures a[0] == \old(a[0]) + 1 and \result == "z"
def bump(a: List[int]) -> str:
    a[0] = a[0] + 1
    return "z"

#@ requires len(xs) == 1 and xs[0] == 0
#@ assigns xs[0]
#@ ensures xs[0] == 0
def f(xs: List[int], s: str) -> str:
    m = max(s, default=bump(xs))
    return "q"

if __name__ == "__main__":
    b = [0]
    f(b, "ab")
    assert b[0] == 0
