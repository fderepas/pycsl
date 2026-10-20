r"""Test 3381 -- route #288 (expected FAIL): census: `b = tid(tid(a)); b[0] = 5; return a[0]` PROVED 1; CPython: 5. Now refused.
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
    b = tid(tid(a))
    b[0] = 5
    return a[0]


if __name__ == "__main__":
    assert f() == 5
