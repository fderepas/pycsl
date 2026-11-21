r"""Test 3395 -- route #290 (expected FAIL): red-team m017/g4: `xs.__imul__(2)`; caller PROVED 23; CPython: 43. Now refused.
"""
# pycsl-expected: FAIL
from typing import List


#@ requires \length(xs) == 2
#@ ensures \result == 1
#@ assigns \nothing
def g(xs: List[int]) -> int:
    xs.__imul__(2)
    return 1


#@ ensures \result == 23
def f() -> int:
    xs: List[int] = [3, 1]
    g(xs)
    return len(xs) * 10 + xs[0]


if __name__ == "__main__":
    assert f() == 43
