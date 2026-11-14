r"""Test 9896 -- W-hash (dict-value-model-r4 §2.5, expected FAIL): `isinstance(v, str)` does NOT narrow a `PyVal` value to hashable when a FILE class derives from `str` (here with `__hash__ = None`): `v` may be an instance of that subclass, so the narrowed site under `no_exception \all` is REFUSED (PYCSL-R349-UNDERIVABLE-HASH-UNDER-CLAIM). CPython raises TypeError for `f(S("a"), 0)`.
"""
# pycsl-expected: FAIL
from typing import Any

PyVal = Any


class S(str):
    __hash__ = None


#@ no_exception \all
#@ ensures \result == n + 1
def f(v: PyVal, n: int) -> int:
    if isinstance(v, str):
        s = {v}
    return n + 1


if __name__ == "__main__":
    try:
        print(f(S("a"), 0))
    except TypeError:
        print("VIOLATION: TypeError under no_exception \\all")
