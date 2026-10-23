r"""Test 1352 — ROUTE #127: `__init_subclass__(cls)` rebinds the subclass's `m` with a NON-LITERAL `setattr(cls, n, ...)` on a PARAMETER (the #119 fence exempted a plain Name receiver); `C().m()` PROVED `\result == 1` while CPython returns 2. Only a local bound from an ordinary call is exempt now.
"""
# pycsl-expected: FAIL
_ = 0  # anchor


class Base:
    def __init__(self) -> None:
        self.a = 0

    def __init_subclass__(cls) -> None:
        n = "m"
        setattr(cls, n, getattr(cls, "n"))

    #@ ensures \result == 1
    #@ assigns \nothing
    def m(self) -> int:
        return 1


class C(Base):
    def __init__(self) -> None:
        self.a = 0

    #@ ensures \result == 2
    #@ assigns \nothing
    def n(self) -> int:
        return 2


#@ ensures \result == 1
#@ assigns \nothing
def f() -> int:
    c = C()
    return c.m()
