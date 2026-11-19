r"""Test 3431 -- route #294 (expected FAIL): `e: Dict[str, PyVal] = func` (a parameter).
The annotated dict local's first assignment discarded its RHS and declared the EMPTY map, so
`"name" in e` PROVED `\result == False`; CPython answers True. Now the RHS is kept.
"""
# pycsl-expected: FAIL
from typing import Any, Dict, List
PyVal = Any


#@ ensures \result == False
#@ assigns \nothing
def g(func: Dict[str, PyVal]) -> bool:
    e: Dict[str, PyVal] = func
    return "name" in e


if __name__ == "__main__":
    assert g({"name": 3}) is True
