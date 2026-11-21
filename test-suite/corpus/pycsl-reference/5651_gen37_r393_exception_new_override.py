r"""Test 5651 -- gen #37 route #393 latent (expected FAIL): `D(Exception)` with a `__new__(cls, a)`; `D()`; PROVED at base 3b2d2e763 (CPython: TypeError, missing `a`). REFUSED (PYCSL-R369-CONSTRUCTOR-ARITY: signature not modelled).
"""
# pycsl-expected: FAIL
class D(Exception):
    def __new__(cls, a: int) -> "D":
        return super().__new__(cls)
#@ no_exception \all
def f() -> int:
    e = D()
    return 1
if __name__ == "__main__":
    print("result", f())
