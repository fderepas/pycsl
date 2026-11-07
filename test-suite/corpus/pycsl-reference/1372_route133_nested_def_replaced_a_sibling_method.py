r"""Test 1372 — ROUTE #133: `C.m` defines a nested `h`, which is lifted to a method of `C` under its own name and REPLACED the method `C.h`: its body became the nested `return 2` and its postcondition was dropped, so the false `C.h` contract `\result == 2` (over `return 1`) and `f() == 2` both PROVED while CPython returns 1.
"""
# pycsl-expected: FAIL
_ = 0  # anchor


class C:
    def __init__(self) -> None:
        self.a = 0

    #@ ensures \result == 2
    #@ assigns \nothing
    def h(self) -> int:
        return 1

    #@ assigns \nothing
    def m(self) -> int:
        def h() -> int:
            return 2
        return 0


#@ ensures \result == 2
#@ assigns \nothing
def f() -> int:
    c = C()
    return c.h()
