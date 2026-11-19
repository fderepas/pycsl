r"""Test 3658 -- gen #37 route #303 (expected FAIL): REFUSAL: `h, k = g, 1; h.add(5); return 5 in g` on a set (L3-tc FAIL at base, now refused at emit).
"""
# pycsl-expected: FAIL
from typing import Set


#@ ensures \result == False
#@ assigns \nothing
def f(n: int) -> bool:
    g: Set[int] = {0}
    h: Set[int] = {0}
    h, k = g, 1
    h.add(5)
    return 5 in g

if __name__ == "__main__":
    assert f(0) == False, f(0)
