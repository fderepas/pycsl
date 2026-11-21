r"""Test 10131 -- run #8 batch B, R1 over-refusal CONTROL (expected PASS): the narrowed PyVal list ITERATED (no slice) under a loop invariant: not refused by PYCSL-R608-PYVAL-SLICE; proves (hoare).
"""
# pycsl-expected: PASS
from typing import Any, Dict, List, Optional, Tuple
PyVal = Any

#@ ensures \result >= 0
#@ assigns \nothing
def f(d: Dict[str, PyVal]) -> int:
    v = d.get("a")
    n = 0
    if isinstance(v, list):
        #@ loop invariant n >= 0
        for e in v:
            n = n + 1
    return n

if __name__ == "__main__":
    print("result", f({"a": [1, 2]}))
