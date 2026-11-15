r"""Test 9992 -- route #604 control (expected PASS; advice of PYCSL-R604-PYVAL-SUBSCRIPT-TYPEERROR-UNDER-CLAIM followed): witness 9976 with the value bound to a name and narrowed (`isinstance(v, dict) and "k" in v`) before `v["k"]`, under `no_exception \all`; `\result == 1` (CPython 1)
"""
# pycsl-expected: PASS
from typing import Any, Dict, List, Optional, Tuple
PyVal = Any


#@ no_exception \all
#@ ensures \result == 1
#@ assigns \nothing
def f(c: int) -> int:
    d: Dict[str, PyVal] = {"a": {"k": "q"}}
    if "a" in d:
        v = d["a"]
        if isinstance(v, dict) and "k" in v:
            if v["k"] == "q":
                return 1
    return 0


if __name__ == "__main__":
    r = f(0)
    print("VIOLATION contract" if r != 1 else "result", r)
