r"""Test 9985 -- route #607 (INTRODUCED, rt59 o15) (expected FAIL: PROVED at int61 c0204b8e1 (rt59 logs), REFUSED PYCSL-R607-PYVAL-BYTES-VALUE at HEAD): `{"a": b"", "e": []}`: the bytes literal is tagged `HArr` of ints, so `b"" == []` (the certified hval_eq) PROVED at int61; CPython False
"""
# pycsl-expected: FAIL
from typing import Any, Dict, List, Optional, Tuple
PyVal = Any

#@ ensures \result == 0
#@ assigns \nothing
def f(c: int) -> int:
    d: Dict[str, PyVal] = {"a": b"", "e": []}
    v = d.get("a")
    if v == d.get("e"):
        return 0
    return 1


if __name__ == "__main__":
    r = f(0)
    print("VIOLATION contract" if r != 0 else "result", r)
