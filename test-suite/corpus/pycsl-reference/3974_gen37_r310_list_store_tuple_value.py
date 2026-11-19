r"""Test 3974 -- gen #37 route #310 (expected FAIL): `ys[0] = (inc(xs), 0)`: the stored display was coerced to `(any int)`; it is now evaluated before the store.
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
    ys: List[Any] = [0]
    ys[0] = (inc(xs), 0)
    return xs[0]

if __name__ == "__main__":
    assert f() == 0
