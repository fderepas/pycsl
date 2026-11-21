r"""Test 9860 — dict-value-model-r4 narrowing (expected PASS): `len(v)` of a value narrowed to `str` is the certified `hval_len (HStr s) = String.length s`.
"""
# pycsl-expected: PASS
from typing import Any, Dict, List, Tuple

PyVal = Any


#@ ensures \result == 1
#@ assigns \nothing
def f(c: int) -> int:
    d: Dict[str, PyVal] = {"a": "x"}
    v = d.get("a")
    if isinstance(v, str):
        return len(v)
    return 0
