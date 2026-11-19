r"""Test 9828 — dict-value-model-r4 law `None != 0` (expected PASS): the honest claim is PROVED under the frozen certified value model. False twin: 9829.
"""
# pycsl-expected: PASS
from typing import Any, Dict, List, Tuple

PyVal = Any


#@ ensures \result == 1
#@ assigns \nothing
def f(c: int) -> int:
    d: Dict[str, PyVal] = {"a": None}
    if d.get("a") != 0:
        return 1
    return 0
