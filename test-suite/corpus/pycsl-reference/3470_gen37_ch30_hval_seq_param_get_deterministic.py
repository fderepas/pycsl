r"""Test 3470 — gen #37 ch30 (expected PASS): a `List[Dict[str, PyVal]]` PARAM is the by-value
`seq hval`; each loop element is a real hval, so two reads of `f.get("name")` agree and the
inner `return 1` is unreachable (CPython: 0 for every input). At acde8476 the param was
`array int` with an opaque `f_get_1`, so the claim timed out.
"""
# pycsl-expected: PASS
from typing import Any, Dict, List

PyVal = Any

#@ ensures \result == 0
#@ assigns \nothing
def recheck(fns: List[Dict[str, PyVal]]) -> int:
    for f in fns:
        if f.get("name") == "c":
            if not (f.get("name") == "c"):
                return 1
    return 0
