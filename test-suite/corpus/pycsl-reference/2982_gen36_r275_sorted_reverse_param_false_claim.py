r"""Test 2982 — route #275 (expected FAIL): for ANY two-element list, `sorted(xs, reverse=True)`
was claimed (and PROVED) ascending. CPython: f([1, 2]) is False.
"""
# pycsl-expected: FAIL
from typing import List


#@ requires len(xs) == 2
#@ ensures \result == True
#@ assigns \nothing
def f(xs: List[int]) -> bool:
    ys = sorted(xs, reverse=True)
    return ys[0] <= ys[1]


if __name__ == "__main__":
    assert f([1, 2]) is False
