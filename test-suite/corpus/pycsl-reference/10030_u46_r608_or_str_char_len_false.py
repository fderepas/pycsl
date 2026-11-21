r"""Test 10030 -- route #608 (PRE-EXISTING, rt60 a01) (expected FAIL: PROVED at lvT dcd13f129 and L9 85c8b0004 (rt60 logs), REFUSED PYCSL-R608-PYVAL-STR-LOWERED-STR-FACT at HEAD): `x = d.get("a") or "z"` is lowered as a `string`, so `len(x[0])` (one character, `str_sub_op`) PROVED `\result == 1` without a claim; CPython f({"a": ["ab"]}) == 2
"""
# pycsl-expected: FAIL
from typing import Any, Dict, List, Optional, Tuple
PyVal = Any

#@ ensures \result == 1
#@ assigns \nothing
def f(d: Dict[str, PyVal]) -> int:
    x = d.get("a") or "z"
    if len(x) > 0:
        return len(x[0])
    return 1

if __name__ == "__main__":
    r = f({"a": ["ab"]})
    print("VIOLATION contract" if r != 1 else "result", r)
