r"""Test 3571 -- gen #37 route #299 (expected FAIL): `bool([*range(0)])` stored as an hval is False in CPython (empty list); the claim that it is truthy is FALSE.
"""
# pycsl-expected: FAIL
from typing import Any, List, Dict, Set, Tuple, Optional
PyVal = Any

#@ ensures \result == 1
#@ assigns \nothing
def g() -> int:
    d: Dict[str, PyVal] = {"a": [*range(0)]}
    if bool(d.get("a")):
        return 1
    return 2

if __name__ == "__main__":
    assert g() != 1, g()
