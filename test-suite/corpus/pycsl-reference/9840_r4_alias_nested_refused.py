r"""Test 9840 — dict-value-model-r4 (impl F4, fr4 P1a) (expected FAIL): `inner` is shared by root["x"] and root["y"]; after `root["x"]["k"] = 1`, `"k" in root["y"]` is True in CPython (returns 1). The r2c escape check refuses the store; the false `ensures` is never proved.
"""
# pycsl-expected: FAIL
from typing import Any, Dict, List, Tuple

PyVal = Any


#@ requires True
#@ ensures \result == 0
#@ assigns \nothing
def alias_nested() -> int:
    inner: Dict[str, PyVal] = {}
    root: Dict[str, PyVal] = {"x": inner, "y": inner}
    root["x"]["k"] = 1
    if "k" in root["y"]:
        return 1
    return 0
