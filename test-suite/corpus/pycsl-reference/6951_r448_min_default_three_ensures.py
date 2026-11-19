r"""Test 6951 -- route #448 (expected FAIL): `min(a, b, default=a)` under `#@ no_exception \all` with `ensures \result <= a`. PROVED on main db6c57253 (red team 36 witness `c11_q081_min_default_three_ensures.py`); CPython raises TypeError (the `__main__` driver prints VIOLATION). Now REFUSED (PYCSL-R441-BUILTIN-SIGNATURE, cross-constraint of route #448).
"""
# pycsl-expected: FAIL
#@ no_exception \all
#@ ensures \result <= a
def f(a: int, b: int) -> int:
    return min(a, b, default=a)


if __name__ == "__main__":
    try:
        r = f(1, 2)
        print("result", r)
    except Exception as e:
        print("VIOLATION", type(e).__name__, e)
