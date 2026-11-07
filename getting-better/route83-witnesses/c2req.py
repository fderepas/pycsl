class C:
    v: int
    #@ assigns self.v
    def __init__(self, n: int) -> None:
        self.v: int = 0
        if n > 0:
            self.v = n

#@ requires m == 0
#@ ensures \result == m
def g(m: int) -> int:
    return m

#@ ensures \result == 0
def f() -> int:
    c = C(7)
    return g(c.v)
if __name__ == "__main__":
    print(f())
