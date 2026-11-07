r"""Test 3387 -- route #289 (expected FAIL): census: an UNANNOTATED tuple `t = (a, 0)`, `b = t[0]; b[0] += 4` PROVED `a[0] == 1`; CPython: 5. Now refused.
"""
# pycsl-expected: FAIL
from typing import List, Tuple


#@ ensures \result == 1
def f() -> int:
    a: List[int] = [1]
    t = (a, 0)
    b = t[0]
    b[0] += 4
    return a[0]


if __name__ == "__main__":
    assert f() == 5
