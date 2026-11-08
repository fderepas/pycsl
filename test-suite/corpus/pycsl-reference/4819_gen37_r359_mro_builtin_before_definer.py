r"""Test 4819 -- gen #37 route #359 (expected FAIL): witness m19 (stdlib form): `class C(float, A): pass` with `A.hex -> int`; float's own `hex` (a str) precedes A in the MRO; `g(a: A)` under `no_exception \all`, `ensures \result == 0` over `a.hex() % 1` PROVED (CPython TypeError: str % int). REFUSED (PYCSL-SEM-OVERRIDE-REFINEMENT: a class from outside the file precedes the defining class).
"""
# pycsl-expected: FAIL
class A:
    def __init__(self) -> None:
        self.n = 0
    def hex(self) -> int:
        return 1

class C(float, A):
    pass

#@ no_exception \all
#@ ensures \result == 0
def g(a: A) -> int:
    return a.hex() % 1


if __name__ == "__main__":
    try:
        g(C())
        assert False, "expected TypeError"
    except TypeError:
        pass
