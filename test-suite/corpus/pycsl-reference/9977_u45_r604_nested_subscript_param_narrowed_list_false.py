r"""Test 9977 -- route #604 (PRE-EXISTING, rt59 d16) (expected FAIL: PROVED at int61 c0204b8e1 (rt59 logs), REFUSED PYCSL-R604-PYVAL-SUBSCRIPT-TYPEERROR-UNDER-CLAIM at HEAD): `d["a"]["k"]` after `isinstance(d["a"], list)` under `no_exception \all` PROVED; CPython TypeError
"""
# pycsl-expected: FAIL
from typing import Any, Dict, List, Optional, Tuple
PyVal = Any

#@ no_exception \all
#@ ensures \result == 0
#@ assigns \nothing
def f(d: Dict[str, PyVal]) -> int:
    if "a" in d:
        v = d["a"]
        if isinstance(v, list):
            x = d["a"]["k"]
    return 0


if __name__ == "__main__":
    try:
        print("result", f({"a": [1]}))
    except Exception as e:
        print("VIOLATION no_exception", type(e).__name__, e)
