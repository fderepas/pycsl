r"""Test 9970 -- route #603 (INTRODUCED, rt59 c01) (expected FAIL: PROVED at int61 c0204b8e1 (rt59 logs), REFUSED PYCSL-R603-PYVAL-STR-LOWERED-TYPE-TEST at HEAD): `x = d.get("a") or "z"` on a local literal dict {"a": 5}: the model types x a `string`, so `isinstance(x, str)` was decided true and `\result == 0` PROVED at int61 c0204b8e1; CPython f(0) == 1
"""
# pycsl-expected: FAIL
from typing import Any, Dict, List, Optional, Tuple
PyVal = Any

#@ ensures \result == 0
#@ assigns \nothing
def f(c: int) -> int:
    d: Dict[str, PyVal] = {"a": 5}
    x = d.get("a") or "z"
    if isinstance(x, str):
        return 0
    return 1

if __name__ == "__main__":
    r = f(0)
    print("VIOLATION contract" if r != 0 else "result", r)
