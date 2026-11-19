r"""Test 3910 -- gen #37 route #307 (expected FAIL): `ys[xs[0]] + inc(xs) * 0` read the index after the call wrote it; Why3 evaluates application arguments right-to-left, Python left-to-right. PROVED before #307 (red-team probe r08_list_index_read_after).
"""
# pycsl-expected: FAIL
from typing import List, Dict

#@ requires len(a) >= 1
#@ assigns a[0]
#@ ensures a[0] == \old(a[0]) + 1 and \result == a[0]
def inc(a: List[int]) -> int:
    a[0] = a[0] + 1
    return a[0]

#@ ensures \result == 11
def f() -> int:
    xs = [0]
    ys = [10, 11, 12]
    return ys[xs[0]] + inc(xs) * 0

if __name__ == "__main__":
    assert f() == 11
