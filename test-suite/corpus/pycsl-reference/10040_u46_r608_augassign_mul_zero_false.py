r"""Test 10040 -- route #608 (u46 probe q12) (expected FAIL: L3-tc failure at base int62 c4159443b, held by accident (u46 report); REFUSED PYCSL-R608-PYVAL-STR-LOWERED-STR-FACT at HEAD): `x *= 0` of a string-lowered `x = d.get("a") or "z"` is the str repeat in the model, then `x == ""`; CPython f({"a": [1]}) is False
"""
# pycsl-expected: FAIL
from typing import Any, Dict, List, Optional, Tuple
PyVal = Any

#@ ensures \result == True
#@ assigns \nothing
def f(d: Dict[str, PyVal]) -> bool:
    x = d.get("a") or "z"
    x *= 0
    return x == ""

if __name__ == "__main__":
    r = f({"a": [1]})
    print("VIOLATION contract" if r != True else "result", r)
