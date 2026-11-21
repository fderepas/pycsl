class P:
    v: int
    #@ assigns self.v
    def __init__(self, v: int = 0) -> None:
        self.v = v

#@ ensures \result == 7
def f() -> int:
    p = P(7)
    return p.v
if __name__ == "__main__":
    print(f())
