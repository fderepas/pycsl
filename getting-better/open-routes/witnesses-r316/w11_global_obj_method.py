class Q:
    def __init__(self) -> None:
        self.n = 0

gq = Q()

class P:
    def __init__(self) -> None:
        self.c = 0
    def bump(self) -> None:
        gq.n = gq.n + 1

#@ ensures \result == 0
def f() -> int:
    a = gq.n
    p = P()
    p.bump()
    return gq.n - a

if __name__ == "__main__":
    assert f() == 0, f()
