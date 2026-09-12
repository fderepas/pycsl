class C:
    n: int
    #@ assigns self.n
    def __init__(self, k: int) -> None:
        self.n = 0
        if k > 0:
            self.n += 5

#@ ensures \result == 0
def f() -> int:
    c = C(7)
    return c.n
