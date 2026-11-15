r"""Test 10039 -- route #608 (PRE-EXISTING, u46 probe q13) (expected FAIL: PROVED at base int62 c4159443b (u46 report), REFUSED PYCSL-R608-PYVAL-STR-LOWERED-STR-FACT at HEAD): `#@ assert len(x[0]) == 1` on a string-lowered `x = d.get("a") or "z"` PROVED (the assert is decided by the str type); CPython len(x[0]) == 2 for {"a": ["ab"]}
"""
# pycsl-expected: FAIL
from typing import Any, Dict, List, Optional, Tuple
PyVal = Any

#@ ensures \result == 1
#@ assigns \nothing
def f(d: Dict[str, PyVal]) -> int:
    x = d.get("a") or "z"
    if len(x) > 0:
        #@ assert len(x[0]) == 1
        return 1
    return 1

if __name__ == "__main__":
    d = {"a": ["ab"]}
    x = d.get("a") or "z"
    print("VIOLATION assert" if len(x[0]) != 1 else "result", f(d))
