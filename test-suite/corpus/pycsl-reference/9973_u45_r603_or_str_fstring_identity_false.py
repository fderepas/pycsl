r"""Test 9973 -- route #603 (rt59 k12) (expected FAIL: PROVED at int61 c0204b8e1 (rt59 logs), REFUSED PYCSL-R603-PYVAL-STR-LOWERED-TYPE-TEST at HEAD): `f"{x}" == x` with x = `d.get("a") or "z"` lowered to `str_eq_op x x`: PROVED; CPython "5" != 5
"""
# pycsl-expected: FAIL
from typing import Any, Dict, List, Optional, Tuple
PyVal = Any

#@ ensures \result == 0
#@ assigns \nothing
def f(d: Dict[str, PyVal]) -> int:
    x = d.get("a") or "z"
    if f"{x}" == x:
        return 0
    return 1


if __name__ == "__main__":
    r = f({"a": 5})
    print("VIOLATION contract" if r != 0 else "result", r)
