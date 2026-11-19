r"""Test 4359 -- gen #37 route #330 (expected PASS): control: a `List[int]` element keeps its int model and the LENGTH of a bare `list` is an int: PROVES.
"""
# pycsl-expected: PASS
from typing import List
#@ requires len(xs) >= 1
#@ ensures \result == True
#@ assigns \nothing
def g(xs: List[int], ys: list) -> bool:
    return xs[0] % 1 == 0 and len(ys) >= 0

if __name__ == "__main__":
    assert g([3], [0.5]) == True
