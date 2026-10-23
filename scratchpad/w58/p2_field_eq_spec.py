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

#@ ensures b.p == b.q
def mk(b: B) -> int:
    return 0
