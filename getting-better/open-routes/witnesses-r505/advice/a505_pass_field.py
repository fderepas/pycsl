# route #505 advice "Pass the fields the method needs instead of `self`": witness d60305 shape, `getv(self.v)` (= control 7993).
class C:
    def __init__(self, v: int) -> None:
        self.v = v

    def m(self) -> int:
        return getv(self.v)


#@ ensures \result == v
def getv(v: int) -> int:
    return v


g = C(1)


#@ ensures \result == g.v
def f(n: int) -> int:
    return g.m()


