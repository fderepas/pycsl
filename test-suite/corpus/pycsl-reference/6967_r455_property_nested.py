r"""Test 6967 -- route #455 (expected FAIL): a function-level `@property def h(a)` called `h(n)`. PROVED on main db6c57253 (red team 36 witness `c21_d002_property_nested.py`); CPython raises TypeError (the `__main__` driver prints VIOLATION). Now REFUSED (PYCSL-R455-DECORATOR-SITE).
"""
# pycsl-expected: FAIL
#@ no_exception \all
def f(n: int) -> int:
    @property
    def h(a: int) -> int:
        return a
    return h(n)


if __name__ == "__main__":
    try:
        r = f(1)
        print("result", r)
    except Exception as e:
        print("VIOLATION", type(e).__name__, e)
