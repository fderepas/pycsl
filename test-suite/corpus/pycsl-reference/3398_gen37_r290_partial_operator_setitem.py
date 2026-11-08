r"""Test 3398 -- route #290 (expected FAIL): census: `functools.partial(operator.setitem, xs)(0, 9)` (a mutator referenced as a VALUE); caller PROVED 23; CPython: 29. Now refused.
"""
# pycsl-expected: FAIL
from typing import List
import functools
import operator


#@ requires \length(xs) == 2
#@ ensures \result == 1
#@ assigns \nothing
def g(xs: List[int]) -> int:
    functools.partial(operator.setitem, xs)(0, 9)
    return 1


#@ ensures \result == 23
def f() -> int:
    xs: List[int] = [3, 1]
    g(xs)
    return len(xs) * 10 + xs[0]


if __name__ == "__main__":
    assert f() == 29
