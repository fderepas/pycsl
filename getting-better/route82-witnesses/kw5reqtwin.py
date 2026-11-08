class P:
    v: int
    #@ assigns self.v
    def __init__(self, *, v: int = 0) -> None:
        self.v = v

#@ requires n == 7
#@ ensures \result == n
def g(n: int) -> int:
    return n

#@ ensures \result == 7
def f() -> int:
    p = P(v=7)
    return g(p.v)
if __name__ == "__main__":
    print(f())
