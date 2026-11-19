r"""Test 2146 — route #237/#238 (expected FAIL): `len(x)` on an hval local was `hval_len x`,
which counts only an `HArr` and reads 0 for every other carrier — so `len({"z": 1})` PROVED
`\result == 0` (CPython: 1). A non-list carrier now has the uninterpreted `hval_len_other`.
"""
# pycsl-expected: FAIL
from typing import Any, Dict

PyVal = Any


#@ ensures \result == 0
#@ assigns \nothing
def f(c: int) -> int:
    d: Dict[str, PyVal] = {"a": {"z": 1}}
    x = d.get("a", {})
    return len(x)
