r"""Test 3578 -- gen #37 route #300 (expected FAIL): a PARAMETER is a binding: `if c == 1: d = [1, 2]` then `len(d)` is 0 for g(0, []); the claim 2 is FALSE.
"""
# pycsl-expected: FAIL
from typing import Any, List, Dict, Set, Tuple, Optional
PyVal = Any

#@ ensures \result == 2
#@ assigns \nothing
def g(c: int, d: List[int]) -> int:
    if c == 1:
        d = [1, 2]
    return len(d)

if __name__ == "__main__":
    assert g(0, []) != 2
