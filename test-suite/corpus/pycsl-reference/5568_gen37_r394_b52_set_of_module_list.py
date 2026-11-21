r"""Test 5568 -- gen #37 route #394 (expected FAIL): module global `{XS}` with `XS = [1]` (CPython TypeError / ValueError; PROVED at base 3b2d2e763). REFUSED (PYCSL-R349-UNHASHABLE-RECORD: the value's class is derived from its source (or refused as unknown)).
"""
# pycsl-expected: FAIL
XS = [1]


#@ no_exception \all
def f() -> int:
    s = {XS}
    return len(s)


if __name__ == "__main__":
    try:
        print("no violation", f())
    except Exception as e:
        print("VIOLATION", type(e).__name__, e)
