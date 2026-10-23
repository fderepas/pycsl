class C:
    n: int
    #@ assigns self.n
    def __init__(self) -> None:
        self.n = 2

#@ ensures \result == 2
def f() -> int:
    c = C()
    return c.n
