r"""Test 6460 -- route #430 (expected FAIL): rg-dict-r3 probe l3d (= the route #430 carrier). A `no_exception \all` caller returns `h(m)`, where the UN-CLAIMED same-file `h` hashes `m.get("a")` (`m: Dict[str, Any]`, an underivable value). PROVED at base 725a1c7e5; CPython raises TypeError (the `__main__` driver prints VIOLATION). Now REFUSED (PYCSL-R430-CALLEE-UNDERIVABLE-HASH).
"""
# pycsl-expected: FAIL
from typing import Dict, Any


#@ ensures \result == 1
def h(m: Dict[str, Any]) -> int:
    s = {m.get("a")}
    return 1


#@ no_exception \all
#@ ensures \result == 1
def caller(m: Dict[str, Any]) -> int:
    return h(m)


if __name__ == "__main__":
    try:
        print(caller({"a": [1]}))
    except TypeError:
        print("VIOLATION: TypeError under no_exception \\all")
