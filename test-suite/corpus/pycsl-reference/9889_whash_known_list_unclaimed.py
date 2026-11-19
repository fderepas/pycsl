r"""Test 9889 -- W-hash (dict-value-model-r4 §2.5, expected FAIL): a value STATICALLY KNOWN to be a list -- a `PyVal`-declared local bound to a list display -- hashed with NO claim stays UNCONDITIONALLY denied (PYCSL-R349-UNHASHABLE-RECORD): the claim-conditional rule covers only a tagged value whose class is unknown. CPython raises TypeError.
"""
# pycsl-expected: FAIL
from typing import Any

PyVal = Any


#@ ensures \result == n + 1
def f(n: int) -> int:
    x: PyVal = [1]
    s = {x}
    return n + 1


if __name__ == "__main__":
    try:
        print(f(0))
    except TypeError:
        print("VIOLATION: TypeError")
