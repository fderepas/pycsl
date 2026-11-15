r"""Test 9990 -- route #603 control (expected PASS; advice of PYCSL-R603-PYVAL-STR-LOWERED-TYPE-TEST followed): witness 9970 with the PyVal value itself narrowed before any `or` default -- `isinstance(v, str)` is the certified tag test, and `\result == 1` (CPython f(0) == 1) is PROVED
"""
# pycsl-expected: PASS
from typing import Any, Dict, List, Optional, Tuple
PyVal = Any


#@ ensures \result == 1
#@ assigns \nothing
def f(c: int) -> int:
    d: Dict[str, PyVal] = {"a": "x"}
    v = d.get("a")
    if isinstance(v, str):
        return 1
    return 0


if __name__ == "__main__":
    r = f(0)
    print("VIOLATION contract" if r != 1 else "result", r)
