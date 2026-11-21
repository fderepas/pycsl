r"""Test 9880 -- W-hash (dict-value-model-r4 §2.5, expected FAIL): an `HArr`-tagged value (`d.get("a")` of a `Dict[str, PyVal]` holding a list) used as a SET ELEMENT under `no_exception \all`. Its class is not derived hashable (no `isinstance` narrows it, no schema types it), so it is REFUSED (PYCSL-R349-UNDERIVABLE-HASH-UNDER-CLAIM). CPython raises TypeError.
"""
# pycsl-expected: FAIL
from typing import Any, Dict

PyVal = Any


#@ no_exception \all
#@ ensures \result == n + 1
def f(n: int) -> int:
    d: Dict[str, PyVal] = {"a": [1]}
    v = d.get("a")
    s = {v}
    return n + 1


if __name__ == "__main__":
    try:
        print(f(0))
    except TypeError:
        print("VIOLATION: TypeError under no_exception \\all")
