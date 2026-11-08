r"""Test 6011 -- gen #37 route #409 (expected FAIL): red team 32 witness `f43_global_stdlib_attr` -- a standard-library object hashed without classifying its real class (PROVED at base 4431ef86f; CPython violates, see the driver). REFUSED (PYCSL-R349-UNHASHABLE-RECORD: a stdlib object is classified by its real class; an unhashable / container object or a method result of a stdlib object is UNKNOWN).
"""
# pycsl-expected: FAIL
import os
E = os.environ


#@ no_exception \all
def f() -> int:
    s = {E}
    return len(s)


if __name__ == "__main__":
    try:
        r = f()
        print("result", r)
    except Exception as e:
        print("VIOLATION", type(e).__name__, e)
