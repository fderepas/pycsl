r"""Test 4003 -- gen #37 route #313 (expected FAIL): `len({0: inc(xs)})` -> `let _ = (any_map ()) in 1`: a dict display outside a map-returning function is `(any_map ())` and its value call vanished.
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
    n = len({0: inc(xs)})
    return xs[0]

if __name__ == "__main__":
    assert f() == 0, f()
