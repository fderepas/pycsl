r"""Test 5566 -- gen #37 route #394 (expected FAIL): `C.XS in s` (a list class attribute as a dict key) (CPython TypeError / ValueError; PROVED at base 3b2d2e763). REFUSED (PYCSL-R349-UNHASHABLE-RECORD: the value's class is derived from its source (or refused as unknown)).
"""
# pycsl-expected: FAIL
class C:
    XS = [1]


#@ no_exception \all
def f(s: dict) -> bool:
    return C.XS in s


if __name__ == "__main__":
    try:
        print("result", f({}))
    except Exception as e:
        print("VIOLATION", type(e).__name__, e)
