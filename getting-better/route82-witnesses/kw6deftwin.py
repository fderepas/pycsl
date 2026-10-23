class P:
    v: int
    #@ assigns self.v
    def __init__(self, *, v: int = 5) -> None:
        self.v = v

#@ ensures \result == 5
def f() -> int:
    p = P()
    return p.v
if __name__ == "__main__":
    print(f())
