r"""Test 3656 -- gen #37 route #303 (expected FAIL): REFUSAL: `h, k = g, 1; h.append(5)` on a list (L3-tc FAIL at base, now refused at emit).
"""
# pycsl-expected: FAIL
from typing import List


#@ ensures \result == 0
#@ assigns \nothing
def f(n: int) -> int:
    g: List[int] = [0]
    h: List[int] = [0]
    h, k = g, 1
    h.append(5)
    return len(g) - 1

if __name__ == "__main__":
    assert f(0) == 0, f(0)
