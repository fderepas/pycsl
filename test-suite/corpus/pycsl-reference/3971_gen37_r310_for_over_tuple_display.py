r"""Test 3971 -- gen #37 route #310 (expected FAIL): `for _ in (inc(xs), 0)`: the iterable display was coerced to `(any int)` and the call vanished; it is now materialised once before the loop.
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
    for _ in (inc(xs), 0):
        pass
    return xs[0]

if __name__ == "__main__":
    assert f() == 0
