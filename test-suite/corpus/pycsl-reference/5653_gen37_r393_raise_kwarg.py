r"""Test 5653 -- gen #37 route #393 latent (expected FAIL): `raise D(k=1)` caught by `except D` returns 1; PROVED at base 3b2d2e763 (CPython: TypeError escapes). REFUSED (PYCSL-R369-CONSTRUCTOR-ARITY).
"""
# pycsl-expected: FAIL
class D(KeyError):
    pass
#@ no_exception \all
def f() -> int:
    try:
        raise D(k=1)
    except D:
        return 1
    return 2
if __name__ == "__main__":
    print("result", f())
