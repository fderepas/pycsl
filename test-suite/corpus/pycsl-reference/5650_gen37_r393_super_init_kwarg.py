r"""Test 5650 -- gen #37 route #393 latent (expected FAIL): `super().__init__(msg=x)` in a `D(Exception)` `__init__` under `no_exception`; PROVED at base 3b2d2e763 (CPython: TypeError, no keyword arguments). REFUSED (PYCSL-R369-CONSTRUCTOR-ARITY).
"""
# pycsl-expected: FAIL
class D(Exception):
    def __init__(self, x: int) -> None:
        super().__init__(msg=x)
#@ no_exception \all
def f() -> int:
    e = D(1)
    return 1
if __name__ == "__main__":
    print("result", f())
