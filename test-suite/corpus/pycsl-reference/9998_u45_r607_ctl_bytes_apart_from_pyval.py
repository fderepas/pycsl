r"""Test 9998 -- route #607 control (expected PASS; advice of PYCSL-R607-PYVAL-BYTES-VALUE followed): a str value in the PyVal dict and a bytes value kept apart from it are admitted
"""
# pycsl-expected: PASS
from typing import Any, Dict, List, Optional, Tuple
PyVal = Any


#@ ensures \result == 1
#@ assigns \nothing
def f(c: int) -> int:
    d: Dict[str, PyVal] = {"a": "xy"}
    v = d.get("a")
    if isinstance(v, str):
        return 1
    return 0


#@ ensures \result == 2
#@ assigns \nothing
def g(c: int) -> int:
    b = b"xy"
    return len(b)


if __name__ == "__main__":
    ok = f(0) == 1 and g(0) == 2
    print("result" if ok else "VIOLATION contract")
