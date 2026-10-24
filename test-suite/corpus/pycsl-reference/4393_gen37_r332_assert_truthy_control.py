r"""Test 4393 -- gen #37 route #332 (expected PASS): CONTROL: `assert xs` under `requires len(xs) >= 1` and `no_exception \all` PROVES.
"""
# pycsl-expected: PASS
from typing import List
#@ requires len(xs) >= 1
#@ ensures \result == 7
#@ assigns \nothing
#@ no_exception \all
def g(xs: List[int]) -> int:
    assert xs
    return 7

if __name__ == "__main__":
    print(g([5]))
