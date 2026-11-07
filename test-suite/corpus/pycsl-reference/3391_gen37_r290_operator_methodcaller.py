r"""Test 3391 -- route #290 (expected FAIL): red-team m006: `operator.methodcaller('reverse')(xs)` (a computed callee, erased whole); caller PROVED 23; CPython: 21. Now refused.
"""
# pycsl-expected: FAIL
from typing import List
import operator


#@ requires \length(xs) == 2
#@ ensures \result == 1
#@ assigns \nothing
def g(xs: List[int]) -> int:
    operator.methodcaller('reverse')(xs)
    return 1


#@ ensures \result == 23
def f() -> int:
    xs: List[int] = [3, 1]
    g(xs)
    return len(xs) * 10 + xs[0]


if __name__ == "__main__":
    assert f() == 21
