r"""Test 3990 -- gen #37 route #311 (expected FAIL): `zs = ys[xs[0]:inc(xs)]` emitted `Array.sub ys (xs[0]) ((inc xs) - xs[0])`; Why3 evaluates arguments right-to-left so the start bound was read AFTER the call (proved `zs[0] == 2`, CPython 1). The bounds are now let-sequenced in Python order.
"""
# pycsl-expected: FAIL
from typing import List, Dict

#@ requires len(a) >= 1
#@ assigns a[0]
#@ ensures a[0] == \old(a[0]) + 1 and \result == a[0]
def inc(a: List[int]) -> int:
    a[0] = a[0] + 1
    return a[0]

#@ ensures \result == 2
def f() -> int:
    xs = [0]
    ys = [1, 2, 3, 4]
    zs = ys[xs[0]:inc(xs)]
    return zs[0]

if __name__ == "__main__":
    assert f() == 2, f()
