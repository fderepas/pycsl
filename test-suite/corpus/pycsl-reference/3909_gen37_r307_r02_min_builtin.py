r"""Test 3909 -- gen #37 route #307 (expected FAIL): `min(inc(xs) * 10, inc(xs))` evaluated builtin arguments right-to-left; Why3 evaluates application arguments right-to-left, Python left-to-right. PROVED before #307 (red-team probe r02_min_builtin).
"""
# pycsl-expected: FAIL
from typing import List, Dict

#@ requires len(a) >= 1
#@ assigns a[0]
#@ ensures a[0] == \old(a[0]) + 1 and \result == a[0]
def inc(a: List[int]) -> int:
    a[0] = a[0] + 1
    return a[0]

#@ ensures \result == 1
def f() -> int:
    xs = [0]
    return min(inc(xs) * 10, inc(xs))

if __name__ == "__main__":
    assert f() == 1
