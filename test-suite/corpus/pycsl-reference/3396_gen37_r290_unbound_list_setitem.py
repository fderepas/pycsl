r"""Test 3396 -- route #290 (expected FAIL): census: the UNBOUND `list.__setitem__(xs, 0, 9)`; caller PROVED 23; CPython: 29. Now refused.
"""
# pycsl-expected: FAIL
from typing import List


#@ requires \length(xs) == 2
#@ ensures \result == 1
#@ assigns \nothing
def g(xs: List[int]) -> int:
    list.__setitem__(xs, 0, 9)
    return 1


#@ ensures \result == 23
def f() -> int:
    xs: List[int] = [3, 1]
    g(xs)
    return len(xs) * 10 + xs[0]


if __name__ == "__main__":
    assert f() == 29
