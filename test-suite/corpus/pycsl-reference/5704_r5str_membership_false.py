r"""Test 5704 -- R5-str (expected FAIL): membership over a `List[str]` is faithful, not a
fresh boolean that could be assumed: `"zz" in xs` for an arbitrary `xs` is not always true
(CPython: `has(["a"])` returns 0), so `\result == 1` must NOT prove.
"""
# pycsl-expected: FAIL
from typing import List


#@ ensures \result == 1
#@ assigns \nothing
def has(xs: List[str]) -> int:
    if "zz" in xs:
        return 1
    return 0
