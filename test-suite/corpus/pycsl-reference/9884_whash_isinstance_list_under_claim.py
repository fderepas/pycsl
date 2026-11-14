r"""Test 9884 -- W-hash (dict-value-model-r4 §2.5, expected FAIL): a `PyVal` value narrowed by `isinstance(v, list)` -- an UNHASHABLE builtin class -- hashed under `no_exception \all` is REFUSED (PYCSL-R349-UNDERIVABLE-HASH-UNDER-CLAIM): narrowing admits only `str` / `int` / `bool` / `float` / `complex` / `bytes` / None. CPython raises TypeError for `f([1], 0)`.
"""
# pycsl-expected: FAIL
from typing import Any

PyVal = Any


#@ no_exception \all
#@ ensures \result == n + 1
def f(v: PyVal, n: int) -> int:
    if isinstance(v, list):
        s = {v}
    return n + 1


if __name__ == "__main__":
    try:
        print(f([1], 0))
    except TypeError:
        print("VIOLATION: TypeError under no_exception \\all")
