r"""Test 9991 -- route #603 control (expected PASS; advice of PYCSL-R603-PYVAL-STR-LAUNDERED-UNDER-CLAIM followed): witness 9974 with the callee narrowing the PyVal value (`return v` only under `isinstance(v, str)`), so `len(name(d))` under `no_exception \all` is honest (CPython: no exception for any d)
"""
# pycsl-expected: PASS
from typing import Any, Dict, List, Optional, Tuple
PyVal = Any


#@ assigns \nothing
def name(d: Dict[str, PyVal]) -> str:
    v = d.get("name")
    if isinstance(v, str):
        return v
    return "anon"


#@ no_exception \all
#@ ensures \result >= 0
#@ assigns \nothing
def f(d: Dict[str, PyVal]) -> int:
    return len(name(d))


if __name__ == "__main__":
    ok = f({"name": 5}) == 4 and f({"name": "ab"}) == 2
    print("result" if ok else "VIOLATION contract", f({"name": 5}), f({"name": "ab"}))
