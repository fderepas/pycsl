r"""Test 9915 -- lvS (expected FAIL): false twin of 9914. The `rec.get("term")` read is the real
projection of each element, so `\result == 0` is FALSE when a record has a non-empty "term"
(CPython: 1) and must NOT prove. Control: 9914.
"""
# pycsl-expected: FAIL
from typing import Any, Dict, List

PyVal = Any


#@ ensures \result == 0
#@ assigns \nothing
def count_terms(records: List[Dict[str, PyVal]]) -> int:
    n = 0
    #@ loop invariant n >= 0
    for rec in records:
        term = rec.get("term") or {}
        if term:
            n = n + 1
    return n


if __name__ == "__main__":
    r = count_terms([{"term": {"a": 1}}, {}, {"term": {}}])
    print("VIOLATION contract" if r != 0 else "result", r)
