r"""Test 6470 -- route R-gate (expected FAIL): rg-dict-r3 S2 witness w01 `f` (the coordinator's get_hash.py): `{m.get("a")}` on `m: Dict[str, Any]` under `no_exception \all`. PROVED at base 725a1c7e5; CPython raises TypeError (the `__main__` driver prints VIOLATION). Now REFUSED (PYCSL-R349-UNDERIVABLE-HASH-UNDER-CLAIM).
"""
# pycsl-expected: FAIL
from typing import Dict, Any


#@ no_exception \all
#@ ensures \result == 1
def f(m: Dict[str, Any]) -> int:
    s = {m.get("a")}
    return 1


if __name__ == "__main__":
    try:
        print(f({"a": [1]}))
    except TypeError:
        print("VIOLATION: TypeError under no_exception \\all")
