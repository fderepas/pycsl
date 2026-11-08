r"""Test 3385 -- route #289 (expected FAIL): census: `t[0][0] = 5` straight into the tuple's list PROVED `a[0] == 1`; CPython: 5. Now refused.
"""
# pycsl-expected: FAIL
from typing import List, Tuple


#@ ensures \result == 1
def f() -> int:
    a: List[int] = [1]
    t: Tuple[List[int], int] = (a, 0)
    t[0][0] = 5
    return a[0]


if __name__ == "__main__":
    assert f() == 5
