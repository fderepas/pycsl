r"""Test 3579 -- gen #37 route #300 (expected FAIL): a literal STRING rebinding after a non-literal first binding: `s = e; if c == 1: s = "ab"; len(s)` is 3 for g(0, "abc"); the claim 2 is FALSE.
"""
# pycsl-expected: FAIL
from typing import Any, List, Dict, Set, Tuple, Optional

#@ ensures \result == 2
#@ assigns \nothing
def g(c: int, e: str) -> int:
    s = e
    if c == 1:
        s = "ab"
    return len(s)

if __name__ == "__main__":
    assert g(0, "abc") != 2
