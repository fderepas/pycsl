class C:
    n: int
    #@ assigns self.n
    def __init__(self) -> None:
        self.n = 1
        self.n = 2
        self.n = 3

#@ ensures \result == 3
def f() -> int:
    c = C()
    return c.n
