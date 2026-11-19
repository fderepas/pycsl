r"""Test 5620 -- gen #37 route #393 (expected FAIL): `class D(ExceptionGroup)`; `D()` under `no_exception`; PROVED at base 3b2d2e763 (CPython: TypeError, `__new__` takes exactly 2 arguments). REFUSED (PYCSL-S1-UNMODELLED-BASE: ExceptionGroup is outside the exception allow-list).
"""
# pycsl-expected: FAIL
class D(ExceptionGroup):
    pass


#@ no_exception \all
def f() -> int:
    e = D()
    return 1


if __name__ == "__main__":
    try:
        print("no violation", f())
    except Exception as e:
        print("VIOLATION", type(e).__name__, e)
