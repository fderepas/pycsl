class C:
    def __init__(self) -> None:
        self.r = 1

class D:
    def __init__(self) -> None:
        self.r = 0.5

#@ ensures \result == True
def f(c: C) -> bool:
    return c.r % 1 == 0

if __name__ == "__main__":
    c = C()
    d = D()
    d.__class__ = C
    assert f(d) == True
