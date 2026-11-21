r"""Test 9882 -- W-hash (dict-value-model-r4 §2.5, expected FAIL): a `PyVal` PARAMETER hashed UN-NARROWED (a set display) under `no_exception \all`. A tagged value is claim-conditional now (it was denied unconditionally as `Any`): under the claim it is REFUSED (PYCSL-R349-UNDERIVABLE-HASH-UNDER-CLAIM). CPython raises TypeError for `f([1], 0)`.
"""
# pycsl-expected: FAIL
from typing import Any

PyVal = Any


#@ no_exception \all
#@ ensures \result == n + 1
def f(v: PyVal, n: int) -> int:
    s = {v}
    return n + 1


if __name__ == "__main__":
    try:
        print(f([1], 0))
    except TypeError:
        print("VIOLATION: TypeError under no_exception \\all")
