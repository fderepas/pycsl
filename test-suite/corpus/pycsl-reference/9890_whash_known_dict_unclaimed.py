r"""Test 9890 -- W-hash (dict-value-model-r4 §2.5, expected FAIL): a `Dict[str, PyVal]` (statically a dict) hashed with NO claim stays UNCONDITIONALLY denied (PYCSL-R349-UNHASHABLE-RECORD). CPython raises TypeError.
"""
# pycsl-expected: FAIL
from typing import Any, Dict

PyVal = Any


#@ ensures \result == n + 1
def f(n: int) -> int:
    d: Dict[str, PyVal] = {"a": 1}
    m = {d}
    return n + 1


if __name__ == "__main__":
    try:
        print(f(0))
    except TypeError:
        print("VIOLATION: TypeError")
