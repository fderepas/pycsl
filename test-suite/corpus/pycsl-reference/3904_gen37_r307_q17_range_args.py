r"""Test 3904 -- gen #37 route #307 (expected FAIL): `range(inc(c), inc(c))` loop header evaluated `stop` before `start` (now REFUSED); Why3 evaluates application arguments right-to-left, Python left-to-right. PROVED before #307 (red-team probe q17_range_args).
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
    c = [0]
    n = 0
    for i in range(inc(c), inc(c)):
        n = n + 1
    return n

if __name__ == "__main__":
    assert f() == 0
