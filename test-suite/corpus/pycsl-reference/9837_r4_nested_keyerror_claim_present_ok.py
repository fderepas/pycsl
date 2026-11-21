r"""Test 9837 — dict-value-model-r4 (impl F6 (ii)) (expected PASS): the same nested read of a PRESENT key discharges the presence obligation. False twin: 9836.
"""
# pycsl-expected: PASS
from typing import Any, Dict, List, Tuple

PyVal = Any


#@ no_exception KeyError
#@ ensures \result == 1
#@ assigns \nothing
def f(c: int) -> int:
    d: Dict[str, PyVal] = {"a": {"k": "q"}}
    r = d["a"]
    if r["k"] == "q":
        return 1
    return 0
