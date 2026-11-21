r"""Test 9824 — dict-value-model-r4 law `1 == 1.0` (expected PASS): the honest claim is PROVED under the frozen certified value model. False twin: 9825.
"""
# pycsl-expected: PASS
from typing import Any, Dict, List, Tuple

PyVal = Any


#@ ensures \result == 1
#@ assigns \nothing
def f(c: int) -> int:
    d: Dict[str, PyVal] = {"a": 1}
    if d.get("a") == 1.0:
        return 1
    return 0
