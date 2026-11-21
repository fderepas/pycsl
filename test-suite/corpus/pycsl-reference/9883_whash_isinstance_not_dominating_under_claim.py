r"""Test 9883 -- W-hash (dict-value-model-r4 §2.5, expected FAIL): an `isinstance(v, str)` test that does NOT hold at the hashing site (its block ends without a jump, so the site runs for every `v`) does not narrow: the leaf goes to #432's flow narrowing, which finds no guard, and it is REFUSED (PYCSL-R349-UNDERIVABLE-HASH-UNDER-CLAIM). CPython raises TypeError for `f([1], 0)`.
"""
# pycsl-expected: FAIL
from typing import Any

PyVal = Any


#@ no_exception \all
#@ ensures \result == n + 1
def f(v: PyVal, n: int) -> int:
    if isinstance(v, str):
        n = n + 0
    s = {v}
    return n + 1


if __name__ == "__main__":
    try:
        print(f([1], 0))
    except TypeError:
        print("VIOLATION: TypeError under no_exception \\all")
