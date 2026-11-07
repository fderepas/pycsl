r"""Test 3372 -- route #288 (expected FAIL): red-team a012: a same-file `\trusted` identity callee, `b[0] = 5; return a[0]` PROVED 1; CPython: 5. Now refused.
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
    a: List[int] = [1]
    b: List[int] = tid(a)
    b[0] = 5
    return a[0]


if __name__ == "__main__":
    assert f() == 5
