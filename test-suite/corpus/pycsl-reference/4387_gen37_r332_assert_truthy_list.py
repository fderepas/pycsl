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
    try:
        print(g([]))
    except (AssertionError, IndexError) as e:
        print("CPython raises", type(e).__name__)
