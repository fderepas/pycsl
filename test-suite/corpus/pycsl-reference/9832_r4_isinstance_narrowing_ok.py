r"""Test 9832 — dict-value-model-r4 law `isinstance narrowing` (expected PASS): the honest claim is PROVED under the frozen certified value model. False twin: 9833.
"""
# pycsl-expected: PASS
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
