r"""Test 9841 — dict-value-model-r4 (impl F4, fr4 P1b) (expected FAIL): `b = a` names one dict object; after `a["k"] = 1`, `"k" in b` is True in CPython (returns 1); the false `ensures` is never proved.
"""
# pycsl-expected: FAIL
from typing import Any, Dict, List, Tuple

PyVal = Any


#@ ensures \result == 0
#@ assigns \nothing
def alias_top() -> int:
    a: Dict[str, int] = {}
    b = a
    a["k"] = 1
    if "k" in b:
        return 1
    return 0
