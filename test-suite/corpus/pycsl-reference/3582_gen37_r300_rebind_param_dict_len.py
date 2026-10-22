r"""Test 3582 -- gen #37 route #300 (expected FAIL): a dict PARAMETER rebound to a literal in one arm: `len(d)` is 0 for g(0, {}); the claim 1 is FALSE.
"""
# pycsl-expected: FAIL
from typing import Any, List, Dict, Set, Tuple, Optional

#@ ensures \result == 1
#@ assigns \nothing
def g(c: int, d: Dict[str, int]) -> int:
    if c == 1:
        d = {"a": 1}
    return len(d)

if __name__ == "__main__":
    assert g(0, {}) != 1
