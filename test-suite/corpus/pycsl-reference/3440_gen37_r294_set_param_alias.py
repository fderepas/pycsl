r"""Test 3440 -- route #294 (expected FAIL): `e: Set[str] = func` (set sibling, census row).
A first-assigned annotated set local must keep its RHS: `"name" in e` must not prove `\result == False`;
CPython answers True.
"""
# pycsl-expected: FAIL
from typing import Set


#@ ensures \result == False
#@ assigns \nothing
def g(func: Set[str]) -> bool:
    e: Set[str] = func
    return "name" in e


if __name__ == "__main__":
    assert g({"name"}) is True
