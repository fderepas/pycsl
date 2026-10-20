r"""Test 3443 -- route #294 (expected FAIL): `s: Set[str] = func` first, `s = set()` on another path.
The first assignment of an emitter-local `Set[str]` was lowered to `StrSet.empty ()` (RHS discarded)
because ANOTHER assignment of the same local is `set()`; `"name" in s` PROVED `\result == False`;
CPython answers True.
"""
# pycsl-expected: FAIL
from typing import Set


#@ requires True
#@ ensures \result == False
#@ assigns \nothing
def g(func: Set[str], c: bool) -> bool:
    s: Set[str] = func
    if c:
        s = set()
    return "name" in s


if __name__ == "__main__":
    assert g({"name"}, False) is True
