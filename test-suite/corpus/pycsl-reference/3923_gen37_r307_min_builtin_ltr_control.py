r"""Test 3923 -- gen #37 route #307 (expected PASS): CONTROL: `min(inc(xs) * 10, inc(xs))` proves the CPython value 2.
"""
# pycsl-expected: PASS
from typing import List, Tuple

#@ requires len(a) >= 1
#@ assigns a[0]
#@ ensures a[0] == \old(a[0]) + 1 and \result == a[0]
def inc(a: List[int]) -> int:
    a[0] = a[0] + 1
    return a[0]

#@ ensures \result == 2
def f() -> int:
    xs = [0]
    return min(inc(xs) * 10, inc(xs))

if __name__ == "__main__":
    assert f() == 2
