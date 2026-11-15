r"""Test 9981 -- route #605 (held by accident before, rt59 b18) (expected FAIL: L3-tc failed BY ACCIDENT at int61 c0204b8e1, REFUSED PYCSL-R605-PYVAL-NEGATIVE-INDEX at HEAD): `v[-1]` of a narrowed PyVal list: `hval_list_nth` maps i <= 0 to the FIRST element (L3-tc failed only by accident); CPython reads the last
"""
# pycsl-expected: FAIL
from typing import Any, Dict, List, Optional, Tuple
PyVal = Any

#@ ensures \result == 1
#@ assigns \nothing
def f(c: int) -> int:
    d: Dict[str, PyVal] = {"a": ["x", "y"]}
    v = d.get("a")
    if isinstance(v, list):
        if v[-1] == "x":
            return 1
    return 0

if __name__ == "__main__":
    r = f(0)
    print("VIOLATION contract" if r != 1 else "result", r)
