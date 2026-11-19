r"""Test 10031 -- route #608 (PRE-EXISTING, rt60 a17) (expected FAIL: PROVED at lvT dcd13f129 and L9 (rt60 logs), REFUSED PYCSL-R608-PYVAL-STR-LOWERED-STR-FACT at HEAD): an element `y = v[0]` of a narrowed PyVal list is lowered as a `string` (`hval_nth_str`), so `len(y[0])` PROVED `\result == 1`; CPython f({"a": [["ab"]]}) == 2
"""
# pycsl-expected: FAIL
from typing import Any, Dict, List, Optional, Tuple
PyVal = Any

#@ ensures \result == 1
#@ assigns \nothing
def f(d: Dict[str, PyVal]) -> int:
    v = d.get("a")
    if isinstance(v, list) and len(v) > 0:
        y = v[0]
        if len(y) > 0:
            return len(y[0])
    return 1

if __name__ == "__main__":
    r = f({"a": [["ab"]]})
    print("VIOLATION contract" if r != 1 else "result", r)
