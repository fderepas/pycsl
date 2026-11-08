class C:
    n: int
    #@ assigns self.n
    def __init__(self) -> None:
        self.n = 1
        self.n = 2

#@ requires m == 1
#@ ensures \result == m
def g(m: int) -> int:
    return m

#@ ensures \result == 1
def f() -> int:
    c = C()
    return g(c.n)
