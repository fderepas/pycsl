r"""Test 6953 -- route #449 (expected FAIL): `parse(path, mode, True)` over `def parse(path, mode)` under `#@ no_exception \all`. PROVED on main db6c57253 (red team 36 witness `c12_u024_realistic_arity.py`); CPython raises TypeError (the `__main__` driver prints VIOLATION). Now REFUSED (PYCSL-R449-CALL-SIGNATURE).
"""
# pycsl-expected: FAIL
def parse(path: str, mode: int) -> int:
    return len(path) + mode


#@ no_exception \all
def f(path: str, mode: int) -> int:
    return parse(path, mode, True)


if __name__ == "__main__":
    try:
        r = f('x', 1)
        print("result", r)
    except Exception as e:
        print("VIOLATION", type(e).__name__, e)
