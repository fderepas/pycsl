r"""Test 4820 -- gen #37 route #359 (expected FAIL): witness m20 (stdlib form): file mixin `class B(float): pass`, `class C(B, A): pass`, `A.hex -> int`; the MRO reaches float's `hex` through B; PROVED (CPython TypeError). REFUSED (PYCSL-SEM-OVERRIDE-REFINEMENT).
"""
# pycsl-expected: FAIL
class A:
    def __init__(self) -> None:
        self.n = 0
    def hex(self) -> int:
        return 1

class B(float):
    pass

class C(B, A):
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
