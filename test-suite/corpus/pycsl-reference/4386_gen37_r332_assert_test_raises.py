r"""Test 4386 -- gen #37 route #332 (expected FAIL): an assert whose TEST raises IndexError (`assert xs[3] == 0 or True`, `len(xs) == 1`) under `no_exception \all` PROVED (CPython raises IndexError). The test is now lowered as program code; FAILS on the index-bounds obligation.
"""
# pycsl-expected: FAIL
from typing import List
#@ requires len(xs) == 1
#@ ensures \result == 7
#@ assigns \nothing
#@ no_exception \all
def g(xs: List[int]) -> int:
    assert xs[3] == 0 or True
    return 7

if __name__ == "__main__":
    try:
        print(g([5]))
    except (AssertionError, IndexError) as e:
        print("CPython raises", type(e).__name__)
