r"""Test 9978 -- route #605 (INTRODUCED, rt59 h10) (expected FAIL: PROVED at int61 c0204b8e1 (rt59 logs), REFUSED PYCSL-R605-PYVAL-INDEX-NO-BOUNDS-VC at HEAD): `ks = tuple(d.get("m") or {})`; `ks[5]` lowered to `hval_nth_str` with no bounds VC: `no_exception IndexError` PROVED at int61; CPython IndexError
"""
# pycsl-expected: FAIL
from typing import Any, Dict, List, Optional, Tuple
PyVal = Any

#@ no_exception IndexError
#@ ensures \result == 0
#@ assigns \nothing
def f(c: int) -> int:
    d: Dict[str, PyVal] = {"m": {"a": 1}}
    ks = tuple(d.get("m") or {})
    if ks[5] == "q":
        return 0
    return 0


if __name__ == "__main__":
    try:
        print("result", f(0))
    except IndexError as e:
        print("VIOLATION no_exception", type(e).__name__, e)
