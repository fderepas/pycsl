r"""Test 9976 -- route #604 (PRE-EXISTING, rt59 d14) (expected FAIL: PROVED at int61 c0204b8e1 (rt59 logs), REFUSED PYCSL-R604-PYVAL-SUBSCRIPT-TYPEERROR-UNDER-CLAIM at HEAD): `d["a"]["k"]` with d["a"] a list under `no_exception \all` PROVED; CPython TypeError
"""
# pycsl-expected: FAIL
from typing import Any, Dict, List, Optional, Tuple
PyVal = Any

#@ no_exception \all
#@ ensures \result == 0
#@ assigns \nothing
def f(c: int) -> int:
    d: Dict[str, PyVal] = {"a": [1]}
    x = d["a"]["k"]
    return 0


if __name__ == "__main__":
    try:
        print("result", f(0))
    except Exception as e:
        print("VIOLATION no_exception", type(e).__name__, e)
