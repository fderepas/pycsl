r"""Test 6006 -- gen #37 route #408 (expected FAIL): red team 32 witness `b02_global_sub_store_main` -- a subscript store on a module list in the `__main__` driver (PROVED at base 4431ef86f; CPython violates, see the driver). REFUSED (PYCSL-R349-UNHASHABLE-RECORD: the store is not a binding; the global is a list whose elements are UNKNOWN).
"""
# pycsl-expected: FAIL
XS = [1, 2]


#@ no_exception \all
def f() -> int:
    s = {XS[0]}
    return len(s)


if __name__ == "__main__":
    XS[0] = [5]
    try:
        r = f()
        print("result", r)
    except Exception as e:
        print("VIOLATION", type(e).__name__, e)
