r"""Test 3583 -- gen #37 route #300 (expected FAIL): a str PARAMETER rebound to a literal in one arm: `len(s)` is 3 for g(0, "abc"); the claim 2 is FALSE.
"""
# pycsl-expected: FAIL
from typing import Any, List, Dict, Set, Tuple, Optional

#@ ensures \result == 2
#@ assigns \nothing
def g(c: int, s: str) -> int:
    if c == 1:
        s = "ab"
    return len(s)

if __name__ == "__main__":
    assert g(0, "abc") != 2
