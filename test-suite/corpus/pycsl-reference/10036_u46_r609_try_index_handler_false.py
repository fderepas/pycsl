r"""Test 10036 -- route #609 (PRE-EXISTING, rt60 d22) (expected FAIL: PROVED at lvT dcd13f129 and L9 (rt60 logs), REFUSED PYCSL-R609-PYVAL-READ-UNDER-HANDLER at HEAD): `try: y = v[0] except IndexError: return 0` on a narrowed PyVal list -- the read `hval_nth_str` has no bounds obligation, so route #171 proves the handler dead and `\result == 1` PROVED; CPython f({"a": []}) == 0
"""
# pycsl-expected: FAIL
from typing import Any, Dict, List, Optional, Tuple
PyVal = Any

#@ ensures \result == 1
#@ assigns \nothing
def f(d: Dict[str, PyVal]) -> int:
    v = d.get("a")
    if isinstance(v, list):
        y = ""
        try:
            y = v[0]
        except IndexError:
            return 0
        return 1
    return 1

if __name__ == "__main__":
    r = f({"a": []})
    print("VIOLATION contract" if r != 1 else "result", r)
