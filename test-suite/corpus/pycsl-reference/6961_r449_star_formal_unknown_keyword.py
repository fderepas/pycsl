r"""Test 6961 -- route #449 (expected FAIL): `g(b=n)` over `def g(*a)` (no `**kwargs`). PROVED on main db6c57253 (red team 36 witness `c26_g000_star_formal_kw.py`); CPython raises TypeError (the `__main__` driver prints VIOLATION). Now REFUSED (PYCSL-R449-CALL-SIGNATURE).
"""
# pycsl-expected: FAIL
def g(*a: int) -> int:
    return len(a)


#@ no_exception \all
def f(n: int) -> int:
    return g(b=n)


if __name__ == "__main__":
    try:
        r = f(1)
        print("result", r)
    except Exception as e:
        print("VIOLATION", type(e).__name__, e)
