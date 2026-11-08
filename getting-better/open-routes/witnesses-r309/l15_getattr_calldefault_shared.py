class K:
    def __init__(self, v: int) -> None:
        self.n = v

#@ ensures \result == 0
def z() -> int:
    return 0

#@ ensures \result == 0
def f() -> int:
    a = K(4)
    b = K(5)
    return getattr(a, "n", z()) - getattr(b, "n", z())

if __name__ == "__main__":
    assert f() == 0
