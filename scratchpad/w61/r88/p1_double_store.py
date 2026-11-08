#@ ensures \result == 1
def f() -> int:
    c = C()
    return c.n

class C:
    n: int
    #@ assigns self.n
    def __init__(self) -> None:
        self.n = 1
        self.n = 2
