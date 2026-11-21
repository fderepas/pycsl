r"""Test 3373 -- route #288 (expected FAIL): red-team a013: `b = ident2(a); b[0] = a[0] + 1; return a[0]` on a PARAMETER, `ensures \result == \old(a[0])` PROVED; CPython: old + 1. Now refused.
"""
# pycsl-expected: FAIL
from typing import List
from multi_file_lib.r288_ident import ident2


#@ requires \length(a) == 1
#@ ensures \result == \old(a[0])
def f(a: List[int]) -> int:
    b = ident2(a)
    b[0] = a[0] + 1
    return a[0]


if __name__ == "__main__":
    assert f([1]) == 2
