class C:
    a: int
    b: int
    def __init__(self, n: int) -> None:
        self.a = n
        self.b = self.a + 1

#@ ensures \result == 0
def f() -> int:
    c = C(5)
    return c.b
if __name__ == "__main__":
    print(f())
