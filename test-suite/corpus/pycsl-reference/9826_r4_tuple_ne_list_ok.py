r"""Test 9826 — dict-value-model-r4 law `(1,) != [1]` (expected PASS): the honest claim is PROVED under the frozen certified value model. False twin: 9827.
"""
# pycsl-expected: PASS
from typing import Any, Dict, List, Tuple

PyVal = Any


#@ ensures \result == 1
#@ assigns \nothing
def f(c: int) -> int:
    d: Dict[str, PyVal] = {"a": (1,), "b": [1]}
    if d.get("a") != d.get("b"):
        return 1
    return 0
