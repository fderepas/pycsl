r"""Test 1667 - ROUTE #189 control (gen #29): the same two-branch shape with ONE LOCAL PER CLASS still proves — each receiver resolves to a single class, so each call site keeps its own callee's contract and the branch-dependent result is provable.
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

    #@ ensures \result == 2
    def get(self) -> int:
        return 2


#@ ensures \result == 1 or \result == 2
def probe(flag: int) -> int:
    if flag > 0:
        d = D()
        return d.get()
    c = C()
    return c.get()
