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
    # CPython ground truth: this call RAISES (see the docstring); no handler, because a
    # handler that can catch AssertionError around an assert is refused (route 16).
    print(g([1]))
