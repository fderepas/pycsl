r"""Test 6956 -- route #449 (expected FAIL): a nested `def h(a)` called `h(n, n)`. PROVED on main db6c57253 (red team 36 witness `c12_u021_nested_arity.py`); CPython raises TypeError (the `__main__` driver prints VIOLATION). Now REFUSED (PYCSL-R449-CALL-SIGNATURE).
"""
# pycsl-expected: FAIL
#@ no_exception \all
def f(n: int) -> int:
    def h(a: int) -> int:
        return a
    return h(n, n)


if __name__ == "__main__":
    try:
        r = f(1)
        print("result", r)
    except Exception as e:
        print("VIOLATION", type(e).__name__, e)
