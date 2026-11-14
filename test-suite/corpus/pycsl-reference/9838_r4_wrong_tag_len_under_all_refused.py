r"""Test 9838 — dict-value-model-r4 (impl F6 (iii), user decision (e)) (expected FAIL, REFUSED `PYCSL-R4-HVAL-WRONG-TAG-UNDER-CLAIM`): `len(v)` of an un-narrowed PyVal value raises TypeError in CPython on an int; TypeError is not a VC class, so the site is refused under `#@ no_exception \all`. Honest twin (narrowed): 9839.
"""
# pycsl-expected: FAIL
from typing import Any, Dict, List, Tuple

PyVal = Any


#@ no_exception \all
#@ ensures \result >= 0
#@ assigns \nothing
def f(d: Dict[str, PyVal]) -> int:
    v = d.get("a")
    return len(v)
