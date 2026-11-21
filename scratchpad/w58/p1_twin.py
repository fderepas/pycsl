class C:
    v: int
    def __init__(self, v: int) -> None:
        self.v = v

class B:
    p: C
    q: C
    def __init__(self, p: C, q: C) -> None:
        self.p = p
        self.q = q

#@ ensures \result.p != \result.q
def mk(n: int) -> B:
    return B(C(n), C(n))
