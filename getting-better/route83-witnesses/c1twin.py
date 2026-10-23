class C:
    v: int
    #@ assigns self.v
    def __init__(self, n: int) -> None:
        self.v: int = 0
        if n > 0:
            self.v: int = n

#@ ensures \result == 7
def f() -> int:
    c = C(7)
    return c.v
if __name__ == "__main__":
    print(f())
