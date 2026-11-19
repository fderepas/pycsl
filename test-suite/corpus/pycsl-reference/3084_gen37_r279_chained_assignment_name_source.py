r"""Test 3084 — route #279 (expected FAIL): `a = b = x` with `x` a list name (no temporary): both targets
are copies of `x`, so `b.append(2)` left `len(a) == 1` PROVED at 72ab1c57. CPython: 2. Now refused.
"""
# pycsl-expected: FAIL
from typing import List


#@ ensures \result == 1
#@ assigns \nothing
def f() -> int:
    x: List[int] = [1]
    a: List[int] = []
    b: List[int] = []
    a = b = x
    b.append(2)
    return len(a)


if __name__ == "__main__":
    assert f() == 2
