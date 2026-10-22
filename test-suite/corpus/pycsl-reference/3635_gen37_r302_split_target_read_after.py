r"""Test 3635 -- gen #37 route #302 (expected FAIL): a `for w in s.split()` loop, target read after, kept the pre-loop `""`; CPython g("ab") == "ab".
"""
# pycsl-expected: FAIL
from typing import Any, List, Dict, Set, Tuple, Optional

#@ requires s == "ab"
#@ ensures \result == ""
#@ assigns \nothing
def g(s: str) -> str:
    w = ""
    for w in s.split():
        pass
    return w

if __name__ == "__main__":
    assert g("ab") == "ab"
