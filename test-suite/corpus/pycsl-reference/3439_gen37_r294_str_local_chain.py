r"""Test 3439 -- route #294 (expected FAIL): `a: Dict[str, str] = func; e: Dict[str, str] = a` (local to local).
The annotated dict local's first assignment discarded its RHS and declared the EMPTY map, so
`"name" in e` PROVED `\result == False`; CPython answers True. Now the RHS is kept.
"""
# pycsl-expected: FAIL
from typing import Dict


#@ ensures \result == False
#@ assigns \nothing
def g(func: Dict[str, str]) -> bool:
    a: Dict[str, str] = func
    e: Dict[str, str] = a
    return "name" in e


if __name__ == "__main__":
    assert g({"name": "x"}) is True
