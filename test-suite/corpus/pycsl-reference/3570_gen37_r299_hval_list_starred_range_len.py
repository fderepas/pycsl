r"""Test 3570 -- gen #37 route #299 (expected FAIL): a Starred element of a list literal stored as an hval is NOT one element: `{"a": [*range(2), 3]}` then `len(d.get("a"))` is 3 in CPython; the claim 2 is FALSE.
"""
# pycsl-expected: FAIL
from typing import Any, List, Dict, Set, Tuple, Optional
PyVal = Any

#@ ensures \result == 2
#@ assigns \nothing
def g() -> int:
    d: Dict[str, PyVal] = {"a": [*range(2), 3]}
    return len(d.get("a"))

if __name__ == "__main__":
    assert g() != 2, g()
