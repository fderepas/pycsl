r"""Test 6473 -- route R-gate (expected FAIL): rg-dict-r3 S2 witness w03 (q6): `seen.add(f.get("name"))` over `funcs: List[Dict[str, Any]]` under `no_exception \all`. PROVED at base 725a1c7e5; CPython raises TypeError (the `__main__` driver prints VIOLATION). Now REFUSED.
"""
# pycsl-expected: FAIL
from typing import Any, Dict, List


#@ no_exception \all
#@ ensures \result == 1
def names(funcs: List[Dict[str, Any]]) -> int:
    seen = set()
    for f in funcs:
        seen.add(f.get("name"))
    return 1


if __name__ == "__main__":
    try:
        print(names([{"name": ["x"]}]))
    except TypeError:
        print("VIOLATION: TypeError under no_exception \\all")
