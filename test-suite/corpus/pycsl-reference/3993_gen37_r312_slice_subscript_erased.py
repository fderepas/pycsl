r"""Test 3993 -- gen #37 route #312 (expected FAIL): `v = ys[0:inc(xs)][0]` -> `subscript_get (any int) 0`: the slice was coerced and inc's write vanished; the slice is now evaluated first (`let _ = <slice> in ..`).
"""
# pycsl-expected: FAIL
from typing import List, Dict

#@ requires len(a) >= 1
#@ assigns a[0]
#@ ensures a[0] == \old(a[0]) + 1 and \result == a[0]
def inc(a: List[int]) -> int:
    a[0] = a[0] + 1
    return a[0]

#@ ensures \result == 0
def f() -> int:
    xs = [0]
    ys = [1, 2, 3, 4]
    v = ys[0:inc(xs)][0]
    return xs[0]

if __name__ == "__main__":
    assert f() == 0, f()
