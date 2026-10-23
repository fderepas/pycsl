_ = 0  # anchor


#@ ensures \result == 99
class C:
    def __init__(self) -> None:
        self.n = 0

    def m(self) -> int:
        return 0


#@ ensures \result == 99
def probe() -> int:
    c = C()
    return c.m()
