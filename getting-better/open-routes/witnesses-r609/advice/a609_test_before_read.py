r"""Test 10048 -- route #609 control (expected PASS; advice of PYCSL-R609-PYVAL-READ-UNDER-HANDLER followed): witness 10036 with the condition tested BEFORE the read and no `try` -- `if len(v) == 0: return 0` then `y = v[0]`; `\result == 1` (CPython f(0) == 1) is PROVED
"""
# pycsl-expected: PASS
from typing import Any, Dict, List, Optional, Tuple
PyVal = Any

#@ ensures \result == 1
#@ assigns \nothing
def f(c: int) -> int:
    d: Dict[str, PyVal] = {"a": [7]}
    v = d.get("a")
    if isinstance(v, list):
        if len(v) == 0:
            return 0
        y = v[0]
        return 1
    return 0

if __name__ == "__main__":
    r = f(0)
    print("VIOLATION contract" if r != 1 else "result", r)
