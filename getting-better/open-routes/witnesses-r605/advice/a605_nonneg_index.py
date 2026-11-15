r"""Test 9994 -- route #605 control (expected PASS; advice of PYCSL-R605-PYVAL-NEGATIVE-INDEX followed): witness 9981 reading the last element by a non-negative literal index under a length guard (no claim): `v[1] == "y"` decides `\result == 1` (CPython 1)
"""
# pycsl-expected: PASS
from typing import Any, Dict, List, Optional, Tuple
PyVal = Any


#@ ensures \result == 1
#@ assigns \nothing
def f(c: int) -> int:
    d: Dict[str, PyVal] = {"a": ["x", "y"]}
    v = d.get("a")
    if isinstance(v, list):
        if v[1] == "y":
            return 1
    return 0


if __name__ == "__main__":
    r = f(0)
    print("VIOLATION contract" if r != 1 else "result", r)
