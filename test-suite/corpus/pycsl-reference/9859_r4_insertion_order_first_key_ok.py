r"""Test 9859 — dict-value-model-r4 insertion order (expected PASS): the FIRST key of `{"b": 1, "a": 2, "b": 3}` is `"b"` (replace-first keeps its position; certified `build_fold_read_back`).
"""
# pycsl-expected: PASS
from typing import Any, Dict, List, Tuple

PyVal = Any


#@ ensures \result == 1
#@ assigns \nothing
def f(c: int) -> int:
    d: Dict[str, PyVal] = {"m": {"b": 1, "a": 2, "b": 3}}
    ks = tuple(d.get("m") or {})
    if ks[0] == "b":
        return 1
    return 0
