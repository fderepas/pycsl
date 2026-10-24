r"""Test 4385 -- gen #37 route #332 (expected FAIL): a failing assert with an EFFECTFUL message (`assert x == 2, xs.pop()`) under `no_exception \all` PROVED (CPython raises: the message runs only on failure). FAILS on the AssertionError obligation.
"""
# pycsl-expected: FAIL
from typing import List
#@ ensures \result == 7
#@ assigns \nothing
#@ no_exception \all
def g(xs: List[int]) -> int:
    x = 1
    assert x == 2, xs.pop()
    return 7

if __name__ == "__main__":
    try:
        print(g([1]))
    except (AssertionError, IndexError) as e:
        print("CPython raises", type(e).__name__)
