r"""Test 9980 -- route #605 (PRE-EXISTING, rt59 h02) (expected FAIL: PROVED at int61 c0204b8e1 (rt59 logs), REFUSED PYCSL-R605-PYVAL-INDEX-NO-BOUNDS-VC at HEAD): `v[5]` of a narrowed PyVal list under `no_exception IndexError` PROVED at int61 and 73fd1874f; CPython IndexError
"""
# pycsl-expected: FAIL
from typing import Any, Dict, List, Optional, Tuple
PyVal = Any

#@ no_exception IndexError
#@ ensures \result == 0
#@ assigns \nothing
def f(d: Dict[str, PyVal]) -> int:
    v = d.get("a")
    if isinstance(v, list):
        x = v[5]
    return 0


if __name__ == "__main__":
    try:
        print("result", f({"a": [1]}))
    except Exception as e:
        print("VIOLATION no_exception", type(e).__name__, e)
