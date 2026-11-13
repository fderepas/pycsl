r"""Test 9836 — dict-value-model-r4 (impl F6 (ii)) (expected FAIL): a NESTED PyVal subscript on an absent key under `#@ no_exception KeyError` carries the presence obligation (it was the silent `(HInt 0)` default); `d["a"]["k"]` with `d = {"a": {}}` raises KeyError in CPython. Honest twin: 9837.
"""
# pycsl-expected: FAIL
from typing import Any, Dict, List, Tuple

PyVal = Any


#@ no_exception KeyError
#@ ensures True
#@ assigns \nothing
def f(c: int) -> int:
    d: Dict[str, PyVal] = {"a": {}}
    r = d["a"]
    if r["k"] == "q":
        return 1
    return 0
