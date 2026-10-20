r"""Test 3384 -- route #289 (expected FAIL): red-team a025: the LOCAL twin, `return a[0]` folded to 1, PROVED; CPython: 5. Now refused.
"""
# pycsl-expected: FAIL
from typing import List, Tuple


#@ ensures \result == 1
def f() -> int:
    a: List[int] = [1]
    t: Tuple[List[int], int] = (a, 0)
    b = t[0]
    b[0] = 5
    return a[0]


if __name__ == "__main__":
    assert f() == 5
