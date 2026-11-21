r"""Test 6957 -- route #449 (expected FAIL): `C.s(n, n)` of `@staticmethod def s(a)`. PROVED on main db6c57253 (red team 36 witness `c12_u026_static_through_class.py`); CPython raises TypeError (the `__main__` driver prints VIOLATION). Now REFUSED (PYCSL-R449-CALL-SIGNATURE).
"""
# pycsl-expected: FAIL
class C:
    @staticmethod
    def s(a: int) -> int:
        return a


#@ no_exception \all
def f(n: int) -> int:
    return C.s(n, n)


if __name__ == "__main__":
    try:
        r = f(1)
        print("result", r)
    except Exception as e:
        print("VIOLATION", type(e).__name__, e)
