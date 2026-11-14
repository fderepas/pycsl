r"""Test 9844 — dict-value-model-r4 route (e2) (expected PASS): a VALUE fact about a nested dict with several literal keys (Alt-Ergo cannot separate string literals, fr4 R5b; Z3 loops on the recursive `pairs_get`, R1) proves through the constructor-triggered certified `pairs_get_nil` / `pairs_get_cons` equations. False twin: 9845.
"""
# pycsl-expected: PASS
from typing import Any, Dict, List, Tuple

PyVal = Any


#@ ensures \result == 3
#@ assigns \nothing
def f(c: int) -> int:
    d: Dict[str, PyVal] = {"m": {"a": 1, "b": 2, "c": 3}}
    m = d.get("m") or {}
    x = m.get("c")
    if x == 3:
        return 3
    return 0
