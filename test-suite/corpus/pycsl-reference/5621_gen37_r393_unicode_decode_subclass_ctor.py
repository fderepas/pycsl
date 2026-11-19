r"""Test 5621 -- gen #37 route #393 (expected FAIL): `class D(UnicodeDecodeError)`; `D("x")` under `no_exception`; PROVED at base 3b2d2e763 (CPython: TypeError, takes exactly 5 arguments). REFUSED (PYCSL-S1-UNMODELLED-BASE).
"""
# pycsl-expected: FAIL
class D(UnicodeDecodeError):
    pass


#@ no_exception \all
def f() -> int:
    e = D("x")
    return 1


if __name__ == "__main__":
    try:
        print("no violation", f())
    except Exception as e:
        print("VIOLATION", type(e).__name__, e)
