r"""Test 3912 -- gen #37 route #307 (expected FAIL): if-condition `x < (x := 1)` ran the walrus before reading `x`; Why3 evaluates application arguments right-to-left, Python left-to-right. PROVED before #307 (red-team probe t05_if_walrus).
"""
# pycsl-expected: FAIL
from typing import List, Dict, Tuple

#@ requires len(a) >= 1
#@ assigns a[0]
#@ ensures a[0] == \old(a[0]) + 1 and \result == a[0]
def inc(a: List[int]) -> int:
    a[0] = a[0] + 1
    return a[0]

#@ ensures \result == 1
def f() -> int:
    x = 0
    if x < (x := 1):
        return 0
    return 1

if __name__ == "__main__":
    assert f() == 1
