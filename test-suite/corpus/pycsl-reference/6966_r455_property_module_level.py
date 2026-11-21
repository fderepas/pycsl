r"""Test 6966 -- route #455 (expected FAIL): a module-level `@property def size(p)` called `size(path)`. PROVED on main db6c57253 (red team 36 witness `c21_d004_property_realistic.py`); CPython raises TypeError (the `__main__` driver prints VIOLATION). Now REFUSED (PYCSL-R455-DECORATOR-SITE).
"""
# pycsl-expected: FAIL
@property
def size(p: str) -> int:
    return len(p)


#@ no_exception \all
def f(path: str) -> int:
    return size(path)


if __name__ == "__main__":
    try:
        r = f('ab')
        print("result", r)
    except Exception as e:
        print("VIOLATION", type(e).__name__, e)
