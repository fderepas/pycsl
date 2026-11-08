r"""Test 3386 -- route #289 (expected FAIL): census: a NESTED tuple `((a, 0), 0)`, `b = t[0][0]; b[0] = 5` PROVED `a[0] == 1`; CPython: 5. Now refused.
"""
# pycsl-expected: FAIL
from typing import List, Tuple


#@ ensures \result == 1
def f() -> int:
    a: List[int] = [1]
    t: Tuple[Tuple[List[int], int], int] = ((a, 0), 0)
    b = t[0][0]
    b[0] = 5
    return a[0]


if __name__ == "__main__":
    assert f() == 5
