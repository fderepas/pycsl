r"""Test 3577 -- gen #37 route #300 (expected FAIL): the loop twin: `d = e; for i in range(c): d = {"a": 1}; len(d)` is 0 for g(0, {}); the claim 1 is FALSE.
"""
# pycsl-expected: FAIL
from typing import Any, List, Dict, Set, Tuple, Optional
PyVal = Any

#@ ensures \result == 1
#@ assigns \nothing
def g(c: int, e: Dict[str, int]) -> int:
    d = e
    for i in range(c):
        d = {"a": 1}
    return len(d)

if __name__ == "__main__":
    assert g(0, {}) != 1
