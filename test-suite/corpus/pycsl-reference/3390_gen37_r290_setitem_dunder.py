r"""Test 3390 -- route #290 (expected FAIL): red-team m005: `xs.__setitem__(0, 9)`; caller PROVED 23; CPython: 29. Now refused (PYCSL-SEM-MUTATION-BY-ANOTHER-NAME).
"""
# pycsl-expected: FAIL
from typing import List


#@ requires \length(xs) == 2
#@ ensures \result == 1
#@ assigns \nothing
def g(xs: List[int]) -> int:
    xs.__setitem__(0, 9)
    return 1


#@ ensures \result == 23
def f() -> int:
    xs: List[int] = [3, 1]
    g(xs)
    return len(xs) * 10 + xs[0]


if __name__ == "__main__":
    assert f() == 29
