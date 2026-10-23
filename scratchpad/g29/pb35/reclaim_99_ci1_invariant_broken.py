_ = 0  # anchor


#@ class invariant self.n >= 0
class C:
    def __init__(self) -> None:
        self.n = 0

    #@ assigns self.n
    def break_it(self) -> int:
        self.n = 0 - 1
        return 0

    def read(self) -> int:
        if self.n >= 0:
            return 1
        return 0


#@ ensures \result == 99
def probe() -> int:
    c = C()
    c.break_it()
    return c.read()
