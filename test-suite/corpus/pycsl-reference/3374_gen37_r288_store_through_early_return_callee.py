r"""Test 3374 -- route #288 (expected FAIL): red-team a015: a VERIFIED same-file callee with an early `return x` (lowered `Return_seq (snapshot x)`, a copy), `b = pick(a, c); b[0] = 5; return a[0]` PROVED 1; CPython: 5. Now refused.
"""
# pycsl-expected: FAIL
from typing import List


#@ requires \length(x) > 0
#@ ensures \length(\result) == \length(x)
#@ assigns \nothing
def pick(x: List[int], y: List[int]) -> List[int]:
    if len(x) > 0:
        return x
    return y


#@ ensures \result == 1
def f() -> int:
    a: List[int] = [1]
    c: List[int] = [2]
    b: List[int] = pick(a, c)
    b[0] = 5
    return a[0]


if __name__ == "__main__":
    assert f() == 5
