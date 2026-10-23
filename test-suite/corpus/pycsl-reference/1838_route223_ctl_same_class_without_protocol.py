r"""Test 1838 — ROUTE #223 CONTROL (expected FAIL): the same code, one token apart.

1837 with the `(Protocol)` base removed. The member is then an ordinary method, its body IS
lowered, and `#@ ensures \result == 99` over `return 1` does not hold — so the file FAILS.

That is what makes 1837 a ROUTE and not a missing feature: the contract checker was never
broken, and inheriting from `Protocol` switched it off.
"""
# pycsl-expected: FAIL
_ = 0  # anchor


class P:
    #@ ensures \result == 99
    def m(self) -> int:
        return 1


class C(P):
    def __init__(self) -> None:
        self.v: int = 0


#@ ensures \result == 99
def use() -> int:
    c = C()
    return c.m()
