r"""Test 9851 — dict-value-model-r4 law `isinstance narrowing` (typed) (expected PASS): the honest claim is PROVED under the frozen certified value model. False twin: 9852.
"""
# pycsl-expected: PASS
# pycsl-flags: --memory-model typed
from typing import Any, Dict, List, Tuple

PyVal = Any


#@ ensures \result == "x"
#@ assigns \nothing
def f(c: int) -> str:
    d: Dict[str, PyVal] = {"a": "x"}
    g = d.get("a")
    if isinstance(g, str):
        return g
    return "?"
