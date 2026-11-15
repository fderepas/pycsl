r"""Test 10032 -- route #608 (PRE-EXISTING, rt60 d01) (expected FAIL: PROVED at lvT dcd13f129 and L9 (rt60 logs), REFUSED PYCSL-R608-PYVAL-STR-LOWERED-STR-FACT at HEAD): iterating a string-lowered `x = d.get("a") or "z"` yields one-character strings in the model, so `for ch in x: return len(ch)` PROVED `\result == 1`; CPython f({"a": ["ab"]}) == 2
"""
# pycsl-expected: FAIL
from typing import Any, Dict, List, Optional, Tuple
PyVal = Any

#@ ensures \result == 1
#@ assigns \nothing
def f(d: Dict[str, PyVal]) -> int:
    x = d.get("a") or "z"
    for ch in x:
        return len(ch)
    return 1

if __name__ == "__main__":
    r = f({"a": ["ab"]})
    print("VIOLATION contract" if r != 1 else "result", r)
