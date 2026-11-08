r"""Test 3379 -- route #288 (expected FAIL): census: an element store inside a LOOP through `b = tid(a)` PROVED `a[0] == 1`; CPython: 5. Now refused.
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
    for i in range(1):
        b[i] = 5
    return a[0]


if __name__ == "__main__":
    assert f() == 5
