r"""Test 3754 -- gen #37 ch34 (expected FAIL): fail-closed fence of 3750: a PARAMETER named like the module-level constant shadows it, so `for op in _OPS` iterates the ARGUMENT (CPython: `has_zz(["zz"])` returns 1). The constant's literal must NOT be substituted: the claim `\result == 0` must NOT prove.
"""
# pycsl-expected: FAIL
from typing import List

_OPS: List[str] = ["ab", "c", "def"]


#@ ensures \result == 0
#@ assigns \nothing
def has_zz(_OPS: List[str]) -> int:
    for op in _OPS:
        if op == "zz":
            return 1
    return 0

