r"""Test 9974 -- route #603 (PRE-EXISTING, rt59 c21) (expected FAIL: PROVED at int61 c0204b8e1 (rt59 logs), REFUSED PYCSL-R603-PYVAL-STR-LAUNDERED-UNDER-CLAIM at HEAD): a `-> str` helper returns `d.get("name") or "anon"`; `len(name(d))` under `no_exception \all` PROVED; CPython TypeError for {"name": 5}
"""
# pycsl-expected: FAIL
from typing import Any, Dict, List, Optional, Tuple
PyVal = Any


#@ assigns \nothing
def name(d: Dict[str, PyVal]) -> str:
    return d.get("name") or "anon"


#@ no_exception \all
#@ ensures \result >= 0
#@ assigns \nothing
def f(d: Dict[str, PyVal]) -> int:
    return len(name(d))


if __name__ == "__main__":
    try:
        print("result", f({"name": 5}))
    except Exception as e:
        print("VIOLATION no_exception", type(e).__name__, e)
