r"""Test 9975 -- route #603 (PRE-EXISTING, rt59 c24) (expected FAIL: PROVED at int61 c0204b8e1 (rt59 logs), REFUSED PYCSL-R603-PYVAL-STR-PASSED-AS-STR at HEAD): `names.append(d.get("name") or "anon")` then `",".join(names)` under `no_exception \all` PROVED; CPython TypeError
"""
# pycsl-expected: FAIL
from typing import Any, Dict, List, Optional, Tuple
PyVal = Any


#@ no_exception \all
#@ ensures \result >= 0
#@ assigns \nothing
def f(d: Dict[str, PyVal]) -> int:
    names: List[str] = []
    names.append(d.get("name") or "anon")
    s = ",".join(names)
    return len(s)


if __name__ == "__main__":
    try:
        print("result", f({"name": 5}))
    except Exception as e:
        print("VIOLATION no_exception", type(e).__name__, e)
