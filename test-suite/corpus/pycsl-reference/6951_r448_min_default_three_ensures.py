r"""Test 6951 -- route #448 (expected FAIL): `min(a, b, c, default=a)` under `#@ no_exception \all` with `ensures \result <= a`. PROVED on main db6c57253 (red team 36 witness `c5_k003.py / c11_q081`); CPython raises TypeError (the `__main__` driver prints VIOLATION). Now REFUSED (PYCSL-R441-BUILTIN-SIGNATURE, cross-constraint of route #448).
"""
# pycsl-expected: FAIL
#@ no_exception \all
#@ ensures \result <= a
def f(a: int, b: int, c: int) -> int:
    return min(a, b, c, default=a)


if __name__ == "__main__":
    try:
        r = f(1, 2, 3)
        print("result", r)
    except Exception as e:
        print("VIOLATION", type(e).__name__, e)
