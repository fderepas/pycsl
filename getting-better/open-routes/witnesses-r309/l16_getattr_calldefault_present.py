class K:
    def __init__(self, v: int) -> None:
        self.n = v

#@ ensures \result == 0
def z() -> int:
    return 0

#@ ensures \result == 0
def f() -> int:
    a = K(4)
    x = getattr(a, "n", z())
    a.n = 9
    y = getattr(a, "n", z())
    return x - y

if __name__ == "__main__":
    assert f() == 0
