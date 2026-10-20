r"""Test 3434 -- route #294 (expected FAIL): `e: Dict[str, List[int]] = func`.
The annotated dict local's first assignment discarded its RHS and declared the EMPTY map, so
`"name" in e` PROVED `\result == False`; CPython answers True. Now the RHS is kept.
"""
# pycsl-expected: FAIL
from typing import Any, Dict, List
PyVal = Any


#@ requires True
#@ ensures \result == False
#@ assigns \nothing
def g(func: Dict[str, List[int]]) -> bool:
    e: Dict[str, List[int]] = func
    return "name" in e


if __name__ == "__main__":
    assert g({"name": [1]}) is True
