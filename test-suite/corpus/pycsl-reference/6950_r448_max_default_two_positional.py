r"""Test 6950 -- route #448 (expected FAIL): `max(a, b, default=0)` under `#@ no_exception \all`. PROVED on main db6c57253 (red team 36 witness `c11_q080_realistic_max_default.py`); CPython raises TypeError (the `__main__` driver prints VIOLATION). Now REFUSED (PYCSL-R441-BUILTIN-SIGNATURE, the row cross-constraint `_XC448` of route #448).
"""
# pycsl-expected: FAIL
#@ no_exception \all
def f(a: int, b: int) -> int:
    return max(a, b, default=0)


if __name__ == "__main__":
    try:
        r = f(3, 4)
        print("result", r)
    except Exception as e:
        print("VIOLATION", type(e).__name__, e)
