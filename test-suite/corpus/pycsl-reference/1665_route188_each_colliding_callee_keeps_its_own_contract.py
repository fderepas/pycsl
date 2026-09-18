r"""Test 1665 - ROUTE #188 control (gen #29): with the suffix made injective, all three colliding-stub call sites keep THEIR OWN callee's contract — `f() == 1`, `g() == 123` and `h() == 441` all prove, where `h()` is the site whose stub name collided with `g()`'s. FAILS at HEAD (the E receiver got D's contract, so `\result == 441` was unprovable).
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

    #@ ensures \result == 123
    def get(self) -> int:
        return 123


class E:
    def __init__(self) -> None:
        self.n = 3

    #@ ensures \result == 441
    def get(self) -> int:
        return 441


#@ ensures \result == 1
def f() -> int:
    o = C()
    return o.get()


#@ ensures \result == 123
def g() -> int:
    o = D()
    return o.get()


#@ ensures \result == 441
def h() -> int:
    o = E()
    return o.get()
