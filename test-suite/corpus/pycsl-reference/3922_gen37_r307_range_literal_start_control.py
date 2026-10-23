r"""Test 3922 -- gen #37 route #307 (expected PASS): CONTROL: `range(0, inc(c))` with a literal start is not order-sensitive and still emits (the header is not refused) and proves `c[0] == 1` after the loop.
"""
# pycsl-expected: PASS
from typing import List, Tuple

#@ requires len(a) >= 1
#@ assigns a[0]
#@ ensures a[0] == \old(a[0]) + 1 and \result == a[0]
def inc(a: List[int]) -> int:
    a[0] = a[0] + 1
    return a[0]

#@ ensures \result == 1
def f() -> int:
    c = [0]
    for i in range(0, inc(c)):
        pass
    return c[0]

if __name__ == "__main__":
    assert f() == 1
