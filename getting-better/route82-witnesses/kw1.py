class P:
    v: int
    #@ assigns self.v
    def __init__(self, *, v: int = 0) -> None:
        self.v = v

#@ ensures \result == 0
def f() -> int:
    p = P(v=7)
    return p.v
if __name__ == "__main__":
    print(f())
