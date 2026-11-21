r"""Test 4310 -- gen #37 route #327 (control, expected PASS): control: a capitalised local `N` whose lowered name `n` collides with nothing. PROVED.
"""
# pycsl-expected: PASS
from typing import List
#@ ensures \result == True
#@ assigns \nothing
def g(xs: List[int]) -> bool:
    N = len(xs)
    m = 0
    return N >= m

if __name__ == "__main__":
    assert g([1, 2]) == True
