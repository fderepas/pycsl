r"""Test 3751 -- gen #37 ch34 (expected FAIL): false twin of 3750: the module-level constant DOES contain "c" (CPython returns 1), so claiming 0 must NOT prove.
"""
# pycsl-expected: FAIL
from typing import List

_OPS: List[str] = ["ab", "c", "def"]


#@ ensures \result == 0
#@ assigns \nothing
def has_c() -> int:
    for op in _OPS:
        if op == "c":
            return 1
    return 0
