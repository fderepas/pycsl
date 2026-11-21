r"""Test 3437 -- route #294 (expected FAIL): `e: Dict[str, str] = mk()` (a call result).
The annotated dict local's first assignment discarded its RHS and declared the EMPTY map, so
`"name" in e` PROVED `\result == False`; CPython answers True. Now the RHS is kept.
"""
# pycsl-expected: FAIL
from typing import Dict


#@ assigns \nothing
def mk() -> Dict[str, str]:
    return {"name": "x"}


#@ ensures \result == False
#@ assigns \nothing
def g() -> bool:
    e: Dict[str, str] = mk()
    return "name" in e


if __name__ == "__main__":
    assert g() is True
