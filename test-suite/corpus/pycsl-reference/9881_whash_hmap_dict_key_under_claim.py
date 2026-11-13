r"""Test 9881 -- W-hash (dict-value-model-r4 §2.5, expected FAIL): an `HMap`-tagged value (`d.get("a")` of a `Dict[str, PyVal]` holding a dict) used as a DICT KEY under `no_exception \all`: REFUSED (PYCSL-R349-UNDERIVABLE-HASH-UNDER-CLAIM). CPython raises TypeError.
"""
# pycsl-expected: FAIL
from typing import Any, Dict

PyVal = Any


#@ no_exception \all
#@ ensures \result == n + 1
def f(n: int) -> int:
    d: Dict[str, PyVal] = {"a": {"b": 1}}
    v = d.get("a")
    m: Dict[PyVal, int] = {}
    m[v] = 1
    return n + 1


if __name__ == "__main__":
    try:
        print(f(0))
    except TypeError:
        print("VIOLATION: TypeError under no_exception \\all")
