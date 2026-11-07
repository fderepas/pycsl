r"""Test 1596 - ROUTE #173 (gen #29): `s = "a"; a, b = s.split(",")` under `#@ no_exception ValueError` PROVED (CPython: ValueError, not enough values to unpack). A tuple unpack whose arity is not static is now refused under a ValueError context.
"""
# pycsl-expected: FAIL
_ = 0  # anchor


#@ no_exception ValueError
#@ ensures \result == 0
def probe() -> int:
    s = "a"
    a, b = s.split(",")
    return 0
