class C:
    def __init__(self, x: int) -> None:
        self.x = x

#@ ensures \result == 0
def f() -> int:
    kw = {"x": 5}
    c = C(**kw)
    return c.x

if __name__ == "__main__":
    print(f())
