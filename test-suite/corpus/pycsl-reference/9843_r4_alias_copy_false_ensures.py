r"""Test 9843 — dict-value-model-r4 (impl F4) (expected FAIL): a value-semantics alias program with a FALSE `ensures`: `e = d.get("m")` and `d["m"]` name one nested dict, so after `e["k"] = 1` the read `d["m"].get("k")` is 1 in CPython (returns 1); the FALSE `\result == 0` is never proved (the store through the alias is refused).
"""
# pycsl-expected: FAIL
from typing import Any, Dict, List, Tuple

PyVal = Any


#@ ensures \result == 0
#@ assigns \nothing
def f(c: int) -> int:
    d: Dict[str, PyVal] = {"m": {}}
    e = d.get("m")
    e["k"] = 1
    m = d.get("m")
    if isinstance(m, dict) and m.get("k") == 1:
        return 1
    return 0
