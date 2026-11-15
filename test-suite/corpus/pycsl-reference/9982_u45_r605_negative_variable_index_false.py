r"""Test 9982 -- route #605 (held by accident before, rt59 b19) (expected FAIL: L3-tc failed BY ACCIDENT at int61 c0204b8e1, REFUSED PYCSL-R605-PYVAL-NEGATIVE-INDEX at HEAD): `ks[i]` with `i = c - 1` (negative for c = 0): the model's element read maps it to the first element; CPython counts from the end
"""
# pycsl-expected: FAIL
from typing import Any, Dict, List, Optional, Tuple
PyVal = Any

#@ ensures \result == 1
#@ assigns \nothing
def f(c: int) -> int:
    d: Dict[str, PyVal] = {"m": {"b": 1, "a": 2}}
    ks = tuple(d.get("m") or {})
    i = c - 1
    if len(ks) == 2 and ks[i] == "b":
        return 1
    return 0

if __name__ == "__main__":
    r = f(0)
    print("VIOLATION contract" if r != 1 else "result", r)
