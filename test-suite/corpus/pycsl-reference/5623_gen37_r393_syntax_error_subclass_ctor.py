r"""Test 5623 -- gen #37 route #393 (expected FAIL): `class D(SyntaxError)`; `D("m", 1)` under `no_exception`; PROVED at base 3b2d2e763 (CPython: TypeError, 'int' object is not iterable). REFUSED (PYCSL-S1-UNMODELLED-BASE).
"""
# pycsl-expected: FAIL
class D(SyntaxError):
    pass


#@ no_exception \all
def f() -> int:
    e = D("m", 1)
    return 1


if __name__ == "__main__":
    try:
        print("result", f())
    except Exception as e:
        print("VIOLATION", type(e).__name__, e)
