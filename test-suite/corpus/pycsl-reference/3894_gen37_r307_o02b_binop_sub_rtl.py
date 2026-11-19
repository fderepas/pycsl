r"""Test 3894 -- gen #37 route #307 (expected FAIL): `inc(xs) - inc(xs)` ran the second call first; Why3 evaluates application arguments right-to-left, Python left-to-right. PROVED before #307 (red-team probe o02b_binop_sub_rtl).
"""
# pycsl-expected: FAIL
from typing import List

#@ requires len(a) >= 1
#@ assigns a[0]
#@ ensures a[0] == \old(a[0]) + 1 and \result == a[0]
def inc(a: List[int]) -> int:
    a[0] = a[0] + 1
    return a[0]

#@ ensures \result == 1
def f() -> int:
    xs = [0]
    r = inc(xs) - inc(xs)
    return r

if __name__ == "__main__":
    assert f() == 1
