r"""Test 9986 -- route #607 (PRE-EXISTING, rt59 o13) (expected FAIL: PROVED at int61 c0204b8e1 (rt59 logs), REFUSED PYCSL-R607-PYVAL-BYTES-VALUE at HEAD): `{"a": b"xy"}` tagged `HArr (HCons (HInt 120) ..)`: `isinstance(v, list)` PROVED true at int61 and 73fd1874f; CPython False
"""
# pycsl-expected: FAIL
from typing import Any, Dict, List, Optional, Tuple
PyVal = Any

#@ ensures \result == 0
#@ assigns \nothing
def f(c: int) -> int:
    d: Dict[str, PyVal] = {"a": b"xy"}
    v = d.get("a")
    if isinstance(v, list):
        return 0
    return 1


if __name__ == "__main__":
    r = f(0)
    print("VIOLATION contract" if r != 0 else "result", r)
