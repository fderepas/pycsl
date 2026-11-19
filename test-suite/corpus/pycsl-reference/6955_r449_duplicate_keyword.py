r"""Test 6955 -- route #449 (expected FAIL): `g(1, 2, b=3)` binds `b` twice. PROVED on main db6c57253 (red team 36 witness `c12_u002_fncall.py`); CPython raises TypeError (the `__main__` driver prints VIOLATION). Now REFUSED (PYCSL-R449-CALL-SIGNATURE).
"""
# pycsl-expected: FAIL
def g(a: int, b: int = 0) -> int:
    return a + b


#@ no_exception \all
def f(n: int) -> int:
    return g(1, 2, b=3)


if __name__ == "__main__":
    try:
        r = f(1)
        print("result", r)
    except Exception as e:
        print("VIOLATION", type(e).__name__, e)
