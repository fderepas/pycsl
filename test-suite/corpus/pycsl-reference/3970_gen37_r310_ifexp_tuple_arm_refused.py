r"""Test 3970 -- gen #37 route #310 (expected FAIL): `t = (inc(xs), 0) if c else (0, 0)`: the conditional arm was coerced to `(any int)` and its call vanished; an arm cannot be hoisted, so it is REFUSED (route #310).
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
    t = (inc(xs), 0) if xs[0] == 0 else (0, 0)
    return xs[0]

if __name__ == "__main__":
    assert f() == 0
