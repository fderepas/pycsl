class C:
    x: int = 5
    def __init__(self) -> None:
        self.x = 10

#@ ensures \result == 10
def f() -> int:
    c = C()
    del c.x
    return c.x
if __name__ == "__main__":
    print(f())
