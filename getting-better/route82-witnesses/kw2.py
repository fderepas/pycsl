class P:
    a: int
    c: int
    #@ assigns self.a, self.c
    def __init__(self, a: int, *, b: int = 0) -> None:
        self.a = a
        self.c = b + 1

#@ ensures \result == 0
def f() -> int:
    p = P(1, b=5)
    return p.c
if __name__ == "__main__":
    print(f())
