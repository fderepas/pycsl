r"""Test 3380 -- route #288 (expected FAIL): census: the returned alias handed to a callee that WRITES its argument (`setfirst(b)`, `assigns x[0]`) PROVED `a[0] == 1`; CPython: 7. Now refused.
"""
# pycsl-expected: FAIL
from typing import List


#@ ensures \length(\result) == \length(x)
#@ assigns \nothing
#@ \trusted
def tid(x: List[int]) -> List[int]:
    return x


#@ requires \length(x) >= 1
#@ assigns x[0]
#@ ensures x[0] == 7
def setfirst(x: List[int]) -> None:
    x[0] = 7


#@ ensures \result == 1
def f() -> int:
    a: List[int] = [1, 2]
    b = tid(a)
    setfirst(b)
    return a[0]


if __name__ == "__main__":
    assert f() == 7
