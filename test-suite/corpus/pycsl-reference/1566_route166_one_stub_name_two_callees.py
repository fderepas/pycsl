r"""Test 1566 - ROUTE #166 (gen #29): `o.get()` on a `C` (ensures `\result == 1`) in one function and on a `D` (ensures `\result == 700`) in another both registered the stub `o_get_0`, and `_add_abstract_op` kept the LONGER declaration - so `f() == 700` PROVED while CPython returns 1. A conflicting declaration now gets its own stub name.
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

    #@ ensures \result == 700
    def get(self) -> int:
        return 700


#@ ensures \result == 700
def f() -> int:
    o = C()
    return o.get()


#@ ensures \result == 700
def g() -> int:
    o = D()
    return o.get()

