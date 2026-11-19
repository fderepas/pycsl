# route #505 advice "call the method on a LOCAL instance, verified by its contract" (= control 7994).
class C:
    def __init__(self, v: int) -> None:
        self.v = v

    #@ ensures \result == self.v
    def m(self) -> int:
        return getv(self)


#@ ensures \result == c.v
def getv(c: C) -> int:
    return c.v


#@ ensures \result == 2
def f(n: int) -> int:
    c = C(2)
    return c.m()


