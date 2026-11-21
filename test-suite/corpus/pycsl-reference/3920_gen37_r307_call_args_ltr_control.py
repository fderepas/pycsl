r"""Test 3920 -- gen #37 route #307 (expected PASS): CONTROL: `sub(inc(xs), inc(xs))` proves the CPython value -1 (arguments left-to-right).
"""
# pycsl-expected: PASS
from typing import List, Tuple

#@ requires len(a) >= 1
#@ assigns a[0]
#@ ensures a[0] == \old(a[0]) + 1 and \result == a[0]
def inc(a: List[int]) -> int:
    a[0] = a[0] + 1
    return a[0]

#@ ensures \result == a - b
def sub(a: int, b: int) -> int:
    return a - b

#@ ensures \result == -1
def f() -> int:
    xs = [0]
    return sub(inc(xs), inc(xs))

if __name__ == "__main__":
    assert f() == -1
