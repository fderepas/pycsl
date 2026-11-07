r"""Test 3897 -- gen #37 route #307 (expected FAIL): in `boom(ys) + inc(xs)` the model ran `inc` before `boom` raised, proving a write Python never performs; Why3 evaluates application arguments right-to-left, Python left-to-right. PROVED before #307 (red-team probe q01b_exc_order).
"""
# pycsl-expected: FAIL
from typing import List, Dict

#@ requires len(a) >= 1
#@ assigns a[0]
#@ ensures a[0] == \old(a[0]) + 1 and \result == a[0]
def inc(a: List[int]) -> int:
    a[0] = a[0] + 1
    return a[0]

#@ requires len(b) >= 1
#@ assigns b[0]
#@ ensures b[0] == 5 and \result == 1
#@ raises ValueError when b[0] == 0
def boom(b: List[int]) -> int:
    if b[0] == 0:
        raise ValueError("x")
    b[0] = 5
    return 1

#@ ensures \result == 1
def f() -> int:
    xs = [0]
    ys = [0]
    try:
        r = boom(ys) + inc(xs)
    except ValueError:
        pass
    return xs[0]

if __name__ == "__main__":
    assert f() == 1
