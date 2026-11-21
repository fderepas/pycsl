r"""Test 3809 -- gen #37 route #306 (expected FAIL): str-keyed form of 3802 (local dict, key present).
"""
# pycsl-expected: FAIL
from typing import List, Dict, TypedDict

#@ requires len(a) >= 1
#@ assigns a[0]
#@ ensures a[0] == \old(a[0]) + 1 and \result == 0
def bump(a: List[int]) -> int:
    a[0] = a[0] + 1
    return 0

#@ requires len(xs) == 1 and xs[0] == 0
#@ assigns xs[0]
#@ ensures xs[0] == 0
def f(xs: List[int]) -> int:
    d: Dict[str, int] = {"a": 1}
    return d.get("a", bump(xs))

if __name__ == "__main__":
    b = [0]
    f(b)
    assert b[0] == 0
