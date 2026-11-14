r"""Test 9855 — dict-value-model-r4 law `True == 1` (store) (expected PASS): the honest claim is PROVED under the frozen certified value model. False twin: 9856.
"""
# pycsl-expected: PASS
# pycsl-flags: --memory-model store
from typing import Any, Dict, List, Tuple

PyVal = Any


#@ ensures \result == 1
#@ assigns \nothing
def f(c: int) -> int:
    d: Dict[str, PyVal] = {"a": True}
    if d.get("a") == 1:
        return 1
    return 0
