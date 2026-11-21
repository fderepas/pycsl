r"""Test 6475 -- route R-gate (expected FAIL): rg-dict-r3 S2 witness w06: `{m.get("a"): 1}` (a dict-display key) under `no_exception \all`. PROVED at base 725a1c7e5; CPython raises TypeError (the `__main__` driver prints VIOLATION). Now REFUSED.
"""
# pycsl-expected: FAIL
from typing import Dict, Any


#@ no_exception \all
#@ ensures \result == 1
def f(m: Dict[str, Any]) -> int:
    d = {m.get("a"): 1}
    return 1


if __name__ == "__main__":
    try:
        print(f({"a": [1]}))
    except TypeError:
        print("VIOLATION: TypeError under no_exception \\all")
