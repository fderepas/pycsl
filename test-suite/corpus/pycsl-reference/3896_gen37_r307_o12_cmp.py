r"""Test 3896 -- gen #37 route #307 (expected FAIL): comparison `inc(xs) < inc(xs)` evaluated its operands right-to-left; Why3 evaluates application arguments right-to-left, Python left-to-right. PROVED before #307 (red-team probe o12_cmp).
"""
# pycsl-expected: FAIL
from typing import List

#@ requires len(a) >= 1
#@ assigns a[0]
#@ ensures a[0] == \old(a[0]) + 1 and \result == a[0]
def inc(a: List[int]) -> int:
    a[0] = a[0] + 1
    return a[0]

#@ ensures \result == False
def f() -> bool:
    xs = [0]
    return inc(xs) < inc(xs)

if __name__ == "__main__":
    assert f() == False
