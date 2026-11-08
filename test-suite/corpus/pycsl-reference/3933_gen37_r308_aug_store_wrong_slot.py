r"""Test 3933 -- gen #37 route #308 (expected FAIL): `ys[inc(c)] += 5`: the store landed in a different slot than the load; now REFUSED.
"""
# pycsl-expected: FAIL
from typing import List, Dict

#@ requires len(a) >= 1
#@ assigns a[0]
#@ ensures a[0] == \old(a[0]) + 1 and \result == a[0]
def inc(a: List[int]) -> int:
    a[0] = a[0] + 1
    return a[0]

#@ ensures \result == 5
def f() -> int:
    c = [0]
    ys = [0, 0, 0, 0]
    ys[inc(c)] += 5
    return ys[2]

if __name__ == "__main__":
    assert f() == 5
