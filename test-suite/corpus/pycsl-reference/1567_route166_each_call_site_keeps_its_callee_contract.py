r"""Test 1567 - ROUTE #166 control (gen #29): with distinct stub names `f() == 1` and `g() == 700` both PROVE (FAILS at HEAD).
"""
_ = 0  # anchor


class C:
    def __init__(self) -> None:
        self.n = 1

    #@ ensures \result == 1
    def get(self) -> int:
        return 1


class D:
    def __init__(self) -> None:
        self.n = 2

    #@ ensures \result == 700
    def get(self) -> int:
        return 700


#@ ensures \result == 1
def f() -> int:
    o = C()
    return o.get()


#@ ensures \result == 700
def g() -> int:
    o = D()
    return o.get()

