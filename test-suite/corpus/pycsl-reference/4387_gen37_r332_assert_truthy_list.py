r"""Test 4387 -- gen #37 route #332 (expected FAIL): `assert xs` on a possibly-empty list under `no_exception \all` PROVED (CPython `g([])` raises AssertionError). FAILS on the AssertionError obligation (Python truthiness `len <> 0`).
"""
# pycsl-expected: FAIL
from typing import List
#@ ensures \result == 7
#@ assigns \nothing
#@ no_exception \all
def g(xs: List[int]) -> int:
    assert xs
    return 7

if __name__ == "__main__":
    # CPython ground truth: this call RAISES (see the docstring); no handler, because a
    # handler that can catch AssertionError around an assert is refused (route 16).
    print(g([]))
