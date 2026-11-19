r"""Test 10034 -- route #608 (PRE-EXISTING, rt60 d24) (expected FAIL: PROVED at lvT dcd13f129 and L9 (rt60 logs), REFUSED PYCSL-R608-PYVAL-STR-LOWERED-STR-FACT at HEAD): `x[0:0] == ""` of a string-lowered `x = d.get("a") or "z"` is a str slice in the model, PROVED `\result == True`; CPython f({"a": [1]}) is False ([] != "")
"""
# pycsl-expected: FAIL
from typing import Any, Dict, List, Optional, Tuple
PyVal = Any

#@ ensures \result == True
#@ assigns \nothing
def f(d: Dict[str, PyVal]) -> bool:
    x = d.get("a") or "z"
    return x[0:0] == ""

if __name__ == "__main__":
    r = f({"a": [1]})
    print("VIOLATION contract" if r != True else "result", r)
