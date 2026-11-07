r"""Test 3907 -- gen #37 route #307 (expected FAIL): `sub(x, (x := 5))` ran the walrus argument before reading `x`; Why3 evaluates application arguments right-to-left, Python left-to-right. PROVED before #307 (red-team probe q18_walrus_arg).
"""
# pycsl-expected: FAIL
from typing import List, Dict

#@ requires len(a) >= 1
#@ assigns a[0]
#@ ensures a[0] == \old(a[0]) + 1 and \result == a[0]
def inc(a: List[int]) -> int:
    a[0] = a[0] + 1
    return a[0]

#@ ensures \result == a - b
def sub(a: int, b: int) -> int:
    return a - b

#@ ensures \result == 0
def f() -> int:
    x = 1
    return sub(x, (x := 5))

if __name__ == "__main__":
    assert f() == 0
