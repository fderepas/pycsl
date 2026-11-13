r"""Test 9826 — dict-value-model-r4 law `(1,) != [1]` (expected FAIL: OPEN LIMIT). The claim is TRUE of CPython but NOT proved: a comparison of two PyVal values is the certified recursive `hval_eq`, which neither Alt-Ergo nor Z3 unfolds in the full theory context (measured: even `hval_eq (HBool true) (HInt 1) = true` times out). Sound (nothing false is proved; twin 9827), value-incomplete. Comparisons against a literal use the certified one-level unfolding lemmas and prove (9822, 9824, 9828).
"""
# pycsl-expected: FAIL
from typing import Any, Dict, List, Tuple

PyVal = Any


#@ ensures \result == 1
#@ assigns \nothing
def f(c: int) -> int:
    d: Dict[str, PyVal] = {"a": (1,), "b": [1]}
    if d.get("a") != d.get("b"):
        return 1
    return 0
