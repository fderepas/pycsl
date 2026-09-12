class C:
    v: int
    #@ assigns self.v
    def __init__(self, n: int) -> None:
        self.v: int = 0
        while self.v < n:
            self.v = n

#@ ensures \result == 0
def f() -> int:
    c = C(7)
    return c.v
if __name__ == "__main__":
    print(f())
