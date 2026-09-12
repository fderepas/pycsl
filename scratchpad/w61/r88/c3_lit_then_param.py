class C:
    n: int
    #@ assigns self.n
    def __init__(self, k: int) -> None:
        self.n = 1
        self.n = k

#@ ensures \result == 1
def f() -> int:
    c = C(7)
    return c.n
