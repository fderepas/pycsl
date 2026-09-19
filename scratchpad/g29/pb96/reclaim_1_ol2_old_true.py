_ = 0  # anchor


class C:
    def __init__(self) -> None:
        self.n = 1

    #@ assigns self.n
    #@ ensures self.n == \old(self.n) + 1
    def inc(self) -> int:
        self.n = self.n + 1
        return 0


#@ ensures \result == 1
def probe() -> int:
    c = C()
    c.inc()
    c.inc()
    return c.n
