r"""Test 9972 -- route #603 (PRE-EXISTING, rt59 v01) (expected FAIL: PROVED at int61 c0204b8e1 (rt59 logs), REFUSED PYCSL-R603-PYVAL-STR-LOWERED-TYPE-TEST at HEAD): `e = v[0]` of a narrowed PyVal list lowers to `hval_nth_str` (a `string`), so `isinstance(e, str)` was decided true: PROVED; CPython e is a dict
"""
# pycsl-expected: FAIL
from typing import Any, Dict, List, Optional, Tuple
PyVal = Any

#@ ensures \result == 0
#@ assigns \nothing
def f(c: int) -> int:
    d: Dict[str, PyVal] = {"a": [{"b": 1}]}
    v = d.get("a")
    if isinstance(v, list):
        e = v[0]
        if isinstance(e, str):
            return 0
        return 1
    return 0


if __name__ == "__main__":
    r = f(0)
    print("VIOLATION contract" if r != 0 else "result", r)
