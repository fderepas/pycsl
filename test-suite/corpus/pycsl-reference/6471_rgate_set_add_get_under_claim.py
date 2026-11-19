r"""Test 6471 -- route R-gate (expected FAIL): rg-dict-r3 S2 witness w01 `g`: `seen.add(f2.get("name"))` (`seen: Set[Any]`) under `no_exception \all`. PROVED at base 725a1c7e5; CPython raises TypeError (the `__main__` driver prints VIOLATION). Now REFUSED.
"""
# pycsl-expected: FAIL
from typing import Dict, Any, Set


#@ no_exception \all
#@ ensures \result == 1
def g(f2: Dict[str, Any], seen: Set[Any]) -> int:
    seen.add(f2.get("name"))
    return 1


if __name__ == "__main__":
    try:
        print(g({"name": [1]}, set()))
    except TypeError:
        print("VIOLATION: TypeError under no_exception \\all")
