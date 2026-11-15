r"""Test 9989 -- route #603 control (expected PASS): an `or "<str>"` default of a PyVal read is only COMPARED with a literal (no type test, no claim): the honest shape stays admitted, and the absent key's literal default decides `\result == 1` (CPython 1)
"""
# pycsl-expected: PASS
from typing import Any, Dict, List, Optional, Tuple
PyVal = Any


#@ ensures \result == 1
#@ assigns \nothing
def f(c: int) -> int:
    d: Dict[str, PyVal] = {"b": 5}
    x = d.get("a") or "z"
    if x == "z":
        return 1
    return 0


if __name__ == "__main__":
    r = f(0)
    print("VIOLATION contract" if r != 1 else "result", r)
