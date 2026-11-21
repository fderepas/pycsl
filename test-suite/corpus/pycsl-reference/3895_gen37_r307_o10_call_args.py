r"""Test 3895 -- gen #37 route #307 (expected FAIL): call arguments `sub(inc(xs), inc(xs))` were evaluated right-to-left; Why3 evaluates application arguments right-to-left, Python left-to-right. PROVED before #307 (red-team probe o10_call_args).
"""
# pycsl-expected: FAIL
from typing import List

#@ requires len(a) >= 1
#@ assigns a[0]
#@ ensures a[0] == \old(a[0]) + 1 and \result == a[0]
def inc(a: List[int]) -> int:
    a[0] = a[0] + 1
    return a[0]

#@ ensures \result == a - b
def sub(a: int, b: int) -> int:
    return a - b

#@ ensures \result == 1
def f() -> int:
    xs = [0]
    return sub(inc(xs), inc(xs))

if __name__ == "__main__":
    assert f() == 1
