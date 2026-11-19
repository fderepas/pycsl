r"""Test 3806 -- gen #37 route #306 (expected FAIL): TypedDict `.get("a", bump(xs))`: the record lowering DROPPED the default, but Python evaluates it (xs[0] becomes 1).
"""
# pycsl-expected: FAIL
from typing import List, TypedDict

class TD(TypedDict):
    a: int

#@ requires len(a) >= 1
#@ assigns a[0]
#@ ensures a[0] == \old(a[0]) + 1 and \result == 0
def bump(a: List[int]) -> int:
    a[0] = a[0] + 1
    return 0

#@ requires len(xs) == 1 and xs[0] == 0
#@ assigns xs[0]
#@ ensures xs[0] == 0
def f(t: TD, xs: List[int]) -> int:
    return t.get("a", bump(xs))

if __name__ == "__main__":
    b = [0]
    f({"a": 5}, b)
    assert b[0] == 0
