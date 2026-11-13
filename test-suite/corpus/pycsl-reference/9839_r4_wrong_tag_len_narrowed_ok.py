r"""Test 9839 — dict-value-model-r4 (impl F6 (iii)) (expected FAIL: OPEN LIMIT -- the claim is TRUE of CPython but the provers time out on it in the full r4 theory context: a value fact through the recursive `pairs_set` / `hpairs_len` fold or `hval_len`; sound, value-incomplete): the same `len` under a dominating `isinstance(v, str)` is the certified `hval_len` of an `HStr` (= `String.length`); the honest `\result >= 0` is NOT proved (simpler control: 9860). Twin: 9838.
"""
# pycsl-expected: FAIL
from typing import Any, Dict, List, Tuple

PyVal = Any


#@ ensures \result >= 0
#@ assigns \nothing
def f(d: Dict[str, PyVal]) -> int:
    v = d.get("a")
    if isinstance(v, str):
        return len(v)
    return 0
