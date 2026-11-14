r"""Test 9853 — dict-value-model-r4 law `absent key vs stored None` (store) (expected PASS): the honest claim is PROVED under the frozen certified value model. False twin: 9854.
"""
# pycsl-expected: PASS
# pycsl-flags: --memory-model store
from typing import Any, Dict, List, Tuple

PyVal = Any


#@ ensures \result == 1
#@ assigns \nothing
def f(c: int) -> int:
    d: Dict[str, PyVal] = {"a": None}
    if d.get("a") is None and d.get("b") is None and "a" in d and "b" not in d:
        return 1
    return 0
