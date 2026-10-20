r"""Test 3441 -- route #294 (expected PASS): CONTROLS: an EMPTY construction keeps the empty base
(`{}` / `dict()` then a store, a non-empty literal), for str / PyVal / List[int] values, and the
str-set `set()` (first and re-assignment) keeps `StrSet.empty ()` and its `.add`.
"""
# pycsl-expected: PASS
from typing import Any, Dict, List, Set
PyVal = Any


#@ ensures \result == True
#@ assigns \nothing
def lit_str() -> bool:
    e: Dict[str, str] = {"name": "x"}
    return "name" in e


#@ ensures \result == False
#@ assigns \nothing
def empty_str() -> bool:
    e: Dict[str, str] = {}
    return "name" in e


#@ ensures \result == False
#@ assigns \nothing
def empty_ctor_str() -> bool:
    e: Dict[str, str] = dict()
    return "name" in e


#@ ensures \result == True
#@ assigns \nothing
def store_str() -> bool:
    e: Dict[str, str] = {}
    e["name"] = "x"
    return "name" in e


#@ ensures \result == False
#@ assigns \nothing
def empty_hval() -> bool:
    e: Dict[str, PyVal] = {}
    return "name" in e


#@ ensures \result == False
#@ assigns \nothing
def empty_listint() -> bool:
    e: Dict[str, List[int]] = {}
    return "name" in e


#@ ensures \result == True
#@ assigns \nothing
def strset_add() -> bool:
    s: Set[str] = set()
    s.add("name")
    return "name" in s


#@ ensures \result == True
#@ assigns \nothing
def strset_reset_add() -> bool:
    s: Set[str] = set()
    s.add("x")
    s = set()
    s.add("name")
    return "name" in s


if __name__ == "__main__":
    assert lit_str() is True
    assert empty_str() is False
    assert empty_ctor_str() is False
    assert store_str() is True
    assert empty_hval() is False
    assert empty_listint() is False
    assert strset_add() is True
    assert strset_reset_add() is True
