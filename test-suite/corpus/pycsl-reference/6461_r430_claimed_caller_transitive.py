r"""Test 6461 -- route #430 (expected FAIL): the #430 shape through an intermediate un-claimed function (`caller` -> `mid` -> `h`, `h` hashes `m.get("k")` into a set via `.add`). PROVED at base 725a1c7e5; CPython raises TypeError (the `__main__` driver prints VIOLATION). Now REFUSED: route #178's summary is transitive.
"""
# pycsl-expected: FAIL
from typing import Dict, Any, Set


#@ ensures \result == 1
def h(m: Dict[str, Any], seen: Set[Any]) -> int:
    seen.add(m.get("k"))
    return 1


#@ ensures \result == 1
def mid(m: Dict[str, Any], seen: Set[Any]) -> int:
    return h(m, seen)


#@ no_exception \all
#@ ensures \result == 1
def caller(m: Dict[str, Any], seen: Set[Any]) -> int:
    return mid(m, seen)


if __name__ == "__main__":
    try:
        print(caller({"k": [1]}, set()))
    except TypeError:
        print("VIOLATION: TypeError under no_exception \\all")
