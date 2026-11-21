r"""Test 6474 -- route R-gate (expected FAIL): rg-dict-r3 S2 witness w05: `v in seen` (`seen: Set[str]`) over `m.values()` (`m: Dict[str, Any]`) under `no_exception \all`. PROVED at base 725a1c7e5; CPython raises TypeError (the `__main__` driver prints VIOLATION). Now REFUSED.
"""
# pycsl-expected: FAIL
from typing import Dict, Any, Set


#@ no_exception \all
#@ ensures \result == 1
def f(m: Dict[str, Any], seen: Set[str]) -> int:
    for v in m.values():
        if v in seen:
            return 1
    return 1


if __name__ == "__main__":
    try:
        print(f({"a": [1]}, set()))
    except TypeError:
        print("VIOLATION: TypeError under no_exception \\all")
