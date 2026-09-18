r"""Test 1664 - ROUTE #188 (gen #29): route #166's disambiguating stub suffix is a 100000-bucket hash of the declaration, and `_add_abstract_op` still resolves a same-name/different-declaration clash by keeping the LONGER one — so two callees whose suffixes collide share one contract again. `D.get` (`\result == 123`) and `E.get` (`\result == 441`) both hash to `_c84185`, and `h()` — an `E` receiver — PROVED `\result == 123` while CPython returns 441. The suffix is now injective per base name.
"""
# pycsl-expected: FAIL
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


#@ ensures \result == 123
def h() -> int:
    o = E()
    return o.get()
