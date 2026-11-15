r"""Test 10046 -- route #608 control (expected PASS; advice of PYCSL-R608-PYVAL-STR-LOWERED-STR-FACT followed): the PyVal value itself is narrowed by `isinstance(v, str)` before any str operation, so `len(v)` is the certified `hstr_len` of the HStr payload and `\result == 2` (CPython f(0) == 2) is PROVED
"""
# pycsl-expected: PASS
from typing import Any, Dict, List, Optional, Tuple
PyVal = Any

#@ ensures \result == 2
#@ assigns \nothing
def f(c: int) -> int:
    d: Dict[str, PyVal] = {"a": "ab"}
    v = d.get("a")
    if isinstance(v, str):
        return len(v)
    return 0

if __name__ == "__main__":
    r = f(0)
    print("VIOLATION contract" if r != 2 else "result", r)
