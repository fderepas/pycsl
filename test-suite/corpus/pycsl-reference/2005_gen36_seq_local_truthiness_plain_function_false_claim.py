r"""Test 2005 — gen #36 (expected FAIL): NON-VACUITY twin of 2004 — `acc` holds one
element, so it is TRUTHY and `\result == 0` must NOT prove.
"""
# pycsl-expected: FAIL
from typing import List


#@ ensures \result == 0
#@ assigns \nothing
def go(k: int) -> int:
    acc: List[str] = []
    acc.append("a")
    if acc:
        return 1
    return 0
