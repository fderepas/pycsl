class C:
    n: int
    #@ assigns self.n
    def __init__(self) -> None:
        self.n = 0
        self.n += 5

#@ ensures \result == 5
def f() -> int:
    c = C()
    return c.n
