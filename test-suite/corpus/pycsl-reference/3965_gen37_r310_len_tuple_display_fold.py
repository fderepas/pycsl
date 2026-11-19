r"""Test 3965 -- gen #37 route #310 (expected FAIL): `n = len((inc(xs), 0))`: `len` of a display folded to 2 from its SHAPE and the call vanished; the display is now evaluated first (`let _ = <display> in 2`).
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
    n = len((inc(xs), 0))
    return xs[0]

if __name__ == "__main__":
    assert f() == 0
