r"""Test 3438 -- route #294 (expected FAIL): `e: Dict[str, str] = func if c else {}` (a conditional).
The annotated dict local's first assignment discarded its RHS and declared the EMPTY map, so
`"name" in e` PROVED `\result == False`; CPython answers True. Now the RHS is kept.
"""
# pycsl-expected: FAIL
from typing import Dict


#@ ensures \result == False
#@ assigns \nothing
def g(func: Dict[str, str], c: bool) -> bool:
    e: Dict[str, str] = func if c else {}
    return "name" in e


if __name__ == "__main__":
    assert g({"name": "x"}, True) is True
