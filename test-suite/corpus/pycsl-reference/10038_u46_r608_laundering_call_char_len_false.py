r"""Test 10038 -- route #608 (PRE-EXISTING, u46 probe q09) (expected FAIL: PROVED at base int62 c4159443b (u46 report), REFUSED PYCSL-R608-PYVAL-STR-LOWERED-STR-FACT at HEAD): `n = name(d)` with `name` returning `d.get("a") or "z"` under `-> str` (a laundering function, route #603) and NO claim: `len(n[0])` (one character) PROVED `\result == 1`; CPython f({"a": ["ab"]}) == 2
"""
# pycsl-expected: FAIL
from typing import Any, Dict, List, Optional, Tuple
PyVal = Any

#@ assigns \nothing
def name(d: Dict[str, PyVal]) -> str:
    return d.get("a") or "z"

#@ ensures \result == 1
#@ assigns \nothing
def f(d: Dict[str, PyVal]) -> int:
    n = name(d)
    if len(n) > 0:
        return len(n[0])
    return 1

if __name__ == "__main__":
    r = f({"a": ["ab"]})
    print("VIOLATION contract" if r != 1 else "result", r)
