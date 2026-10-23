r"""Test 3921 -- gen #37 route #307 (expected PASS): CONTROL: returned tuple `c[0], inc(c)` proves the CPython value (0, 1).
"""
# pycsl-expected: PASS
from typing import List, Tuple

#@ requires len(a) >= 1
#@ assigns a[0]
#@ ensures a[0] == \old(a[0]) + 1 and \result == a[0]
def inc(a: List[int]) -> int:
    a[0] = a[0] + 1
    return a[0]

#@ ensures \result[0] == 0 and \result[1] == 1
def f() -> Tuple[int, int]:
    c = [0]
    return c[0], inc(c)

if __name__ == "__main__":
    t = f()
    assert t[0] == 0 and t[1] == 1
