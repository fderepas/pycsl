class C:
    n: int
    #@ assigns self.n
    def __init__(self, k: int) -> None:
        self.n = k
        self.n = 3

#@ ensures \result == 7
def f() -> int:
    c = C(7)
    return c.n
