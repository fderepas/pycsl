class C:
    x: int
    def __init__(self, n: int) -> None:
        self.x = n + 1

#@ ensures \result == 0
def f() -> int:
    c = C(5)
    return c.x
if __name__ == "__main__":
    print(f())
