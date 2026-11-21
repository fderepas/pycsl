r"""Test 3573 -- gen #37 route #299 (expected FAIL): a starred record list through the ch30 hval_to_seq bridge has 3 records in CPython; the claim 2 is FALSE.
"""
# pycsl-expected: FAIL
from typing import Any, List, Dict, Set, Tuple, Optional
PyVal = Any

#@ ensures \result == len(fns)
#@ assigns \nothing
def cnt(fns: List[Dict[str, PyVal]]) -> int:
    return len(fns)

#@ ensures \result == 2
#@ assigns \nothing
def g() -> int:
    holder: Dict[str, PyVal] = {"records": [*({"b": 1}, {"c": 1}), {"a": 1}]}
    return cnt(holder.get("records", []))

if __name__ == "__main__":
    assert g() != 2, g()
