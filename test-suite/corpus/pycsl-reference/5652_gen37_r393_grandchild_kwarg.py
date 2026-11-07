r"""Test 5652 -- gen #37 route #393 latent (expected FAIL): `D(B(ValueError))`; `D(code=1)`; PROVED at base 3b2d2e763 (CPython: TypeError). REFUSED (PYCSL-R369-CONSTRUCTOR-ARITY).
"""
# pycsl-expected: FAIL
class B(ValueError):
    pass
class D(B):
    pass
#@ no_exception \all
def f() -> int:
    e = D(code=1)
    return 1
if __name__ == "__main__":
    print("result", f())
