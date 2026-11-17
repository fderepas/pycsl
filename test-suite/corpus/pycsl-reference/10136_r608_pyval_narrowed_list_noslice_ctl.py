r"""Test 10136 -- run #8 batch B, R1 over-refusal CONTROL (expected PASS): a PyVal value narrowed by `isinstance(v, list)` and not sliced: not refused by PYCSL-R608-PYVAL-SLICE; proves x3 (hoare / typed / store).
"""
# pycsl-expected: PASS
from typing import Any, Dict, List, Optional, Tuple
PyVal = Any

#@ ensures \result == 1
#@ assigns \nothing
def f(d: Dict[str, PyVal]) -> int:
    v = d.get("a")
    if isinstance(v, list):
        return 1
    return 1

if __name__ == "__main__":
    print("result", f({"a": [1, 2]}))
