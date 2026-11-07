_ = 0  # anchor


class C:
    def __init__(self) -> None:
        self.n = 5

    #@ assigns self.n
    #@ act zero:
    #@     given self.n == 0
    #@     ensures self.n == 1
    def bump(self) -> int:
        self.n = self.n + 1
        return 0


#@ ensures \result == 0
def probe() -> int:
    c = C()
    c.bump()
    return c.n
