r"""Test 3378 -- route #288 (expected FAIL): census: a SLICE store `b[0:1] = [9]` through `b = tid(a)` PROVED `a[0] == 1`; CPython: 9. Now refused.
"""
# pycsl-expected: FAIL
from typing import List


#@ ensures \length(\result) == \length(x)
#@ assigns \nothing
#@ \trusted
def tid(x: List[int]) -> List[int]:
    return x


#@ ensures \result == 1
def f() -> int:
    a: List[int] = [1, 2]
    b = tid(a)
    b[0:1] = [9]
    return a[0]


if __name__ == "__main__":
    assert f() == 9
