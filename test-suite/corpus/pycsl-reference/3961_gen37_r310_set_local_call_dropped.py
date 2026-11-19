r"""Test 3961 -- gen #37 route #310 (expected FAIL): `s = {inc(xs)}`: the erased set binding dropped the call; now evaluated before the value is erased.
"""
# pycsl-expected: FAIL
from typing import List, Tuple, Any, Set, Dict

#@ requires len(a) >= 1
#@ assigns a[0]
#@ ensures a[0] == \old(a[0]) + 1 and \result == a[0]
def inc(a: List[int]) -> int:
    a[0] = a[0] + 1
    return a[0]

#@ ensures \result == 0
def f() -> int:
    xs = [0]
    s = {inc(xs)}
    return xs[0]

if __name__ == "__main__":
    assert f() == 0
