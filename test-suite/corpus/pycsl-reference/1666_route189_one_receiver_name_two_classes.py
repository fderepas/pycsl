r"""Test 1666 - ROUTE #189 (gen #29): a local bound to `D()` on one branch and `C()` on the other resolves to ONE class — the last the scanner reaches — so the single call site `o.get()` carried `C.get`'s `ensures` on every path and `\result == 1` PROVED for every `flag` while CPython returns 2 when `flag > 0`. A function that binds one name to two record classes and then calls a method on it is now refused (PYCSL-R189-AMBIGUOUS-RECEIVER-CLASS).
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

    #@ ensures \result == 2
    def get(self) -> int:
        return 2


#@ ensures \result == 1
def probe(flag: int) -> int:
    if flag > 0:
        o = D()
    else:
        o = C()
    return o.get()
