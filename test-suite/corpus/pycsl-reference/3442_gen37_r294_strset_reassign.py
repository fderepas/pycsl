r"""Test 3442 -- route #294 (expected FAIL): `s: Set[str] = set(); s = func` (str-set reassignment).
An emitter-local `Set[str]` (annotated `Set[str]` and somewhere `= set()`) lowered EVERY assignment
to `StrSet.empty ()`, discarding the RHS, so `"name" in s` PROVED `\result == False`; CPython
answers True. Now only `set()` is the empty set; any other RHS is kept.
"""
# pycsl-expected: FAIL
from typing import Set


#@ requires True
#@ ensures \result == False
#@ assigns \nothing
def g(func: Set[str]) -> bool:
    s: Set[str] = set()
    s = func
    return "name" in s


if __name__ == "__main__":
    assert g({"name"}) is True
