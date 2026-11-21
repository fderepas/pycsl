r"""Test 3471 — gen #37 ch30 (expected FAIL): 3470 with `\result == 1`: false in CPython
(`recheck([])` is 0); the seq param must not make the body vacuous.
"""
# pycsl-expected: FAIL
from typing import Any, Dict, List

PyVal = Any

#@ ensures \result == 1
#@ assigns \nothing
def recheck(fns: List[Dict[str, PyVal]]) -> int:
    for f in fns:
        if f.get("name") == "c":
            if not (f.get("name") == "c"):
                return 1
    return 0
