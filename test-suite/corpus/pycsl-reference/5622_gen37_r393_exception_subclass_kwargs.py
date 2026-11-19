r"""Test 5622 -- gen #37 route #393 (expected FAIL): `class D(Exception)`; `D(x=1)` under `no_exception`; PROVED at base 3b2d2e763 (CPython: TypeError, takes no keyword arguments). REFUSED (PYCSL-R369-CONSTRUCTOR-ARITY against the `(self, *args)` signature).
"""
# pycsl-expected: FAIL
class D(Exception):
    pass


#@ no_exception \all
def f() -> int:
    e = D(x=1)
    return 1


if __name__ == "__main__":
    try:
        print("no violation", f())
    except Exception as e:
        print("VIOLATION", type(e).__name__, e)
