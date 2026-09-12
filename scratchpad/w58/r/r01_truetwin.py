class C:
    v: int
    def __init__(self, v: int) -> None:
        self.v = v

#@ ensures \result == 2
def f() -> int:
    a = C(1)
    b = a
    b.v = 2
    return a.v
if __name__ == "__main__":
    print(f())
