r"""Test 9842 — dict-value-model-r4 (impl F4, fr4 P1c) (expected FAIL): `d["x"]` and `d["y"]` may be the SAME object at the call site; a store into a PARAMETER root is refused (family M stays trusted).
"""
# pycsl-expected: FAIL
from typing import Any, Dict, List, Tuple

PyVal = Any


#@ requires True
#@ ensures \result == 0
#@ assigns d
def alias_param(d: Dict[str, PyVal]) -> int:
    d["x"]["k"] = 1
    y = d.get("y") or {}
    if "k" in y:
        return 1
    return 0
