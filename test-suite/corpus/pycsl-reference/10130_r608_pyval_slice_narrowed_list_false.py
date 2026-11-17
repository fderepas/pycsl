r"""Test 10130 -- run #8 batch B, u48 rule R1 (expected FAIL): a SLICE `v[0:0]` of a PyVal value narrowed by `isinstance(v, list)` compared with `""` (route #608 residual q05): CPython `[] == ""` is False, so f({"a": [1, 2]}) returns 0, not 1. The value model has no slice of an `hval` (held only by an L3-tc failure before). REFUSED: PYCSL-R608-PYVAL-SLICE.
"""
# pycsl-expected: FAIL
from typing import Any, Dict, List, Optional, Tuple
PyVal = Any

#@ ensures \result == 1
#@ assigns \nothing
def f(d: Dict[str, PyVal]) -> int:
    v = d.get("a")
    if isinstance(v, list):
        s = v[0:0]
        if s == "":
            return 1
        return 0
    return 1

if __name__ == "__main__":
    r = f({"a": [1, 2]})
    print("VIOLATION contract" if r != 1 else "result", r)
