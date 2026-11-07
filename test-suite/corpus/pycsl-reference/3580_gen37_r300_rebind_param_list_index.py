r"""Test 3580 -- gen #37 route #300 (expected FAIL): a PARAMETER rebound to a literal in one arm must not fold the element read: `if c == 1: d = [5, 6]` then `d[0]` is 7 for g(0, [7]); the claim 5 is FALSE.
"""
# pycsl-expected: FAIL
from typing import Any, List, Dict, Set, Tuple, Optional

#@ ensures \result == 5
#@ assigns \nothing
def g(c: int, d: List[int]) -> int:
    if c == 1:
        d = [5, 6]
    return d[0]

if __name__ == "__main__":
    assert g(0, [7]) != 5
