r"""Test 3905 -- gen #37 route #307 (expected FAIL): `range(inc(c), inc(c) + 5)` loop header evaluated `stop` before `start` (now REFUSED); Why3 evaluates application arguments right-to-left, Python left-to-right. PROVED before #307 (red-team probe q17b_range_first_iter).
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
    c = [0]
    for i in range(inc(c), inc(c) + 5):
        return i
    return -1

if __name__ == "__main__":
    assert f() == 2
