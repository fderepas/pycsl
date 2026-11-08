r"""Test 3995 -- gen #37 route #312 (expected FAIL): `for v in ys[0:inc(xs)]` -> `iter_length (any int)`, the call vanished; the iterable is now materialised before the loop.
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
    for v in ys[0:inc(xs)]:
        pass
    return xs[0]

if __name__ == "__main__":
    assert f() == 0, f()
