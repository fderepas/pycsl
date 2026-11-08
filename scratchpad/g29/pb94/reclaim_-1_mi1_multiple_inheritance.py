_ = 0  # anchor


class A:
    def __init__(self) -> None:
        self.n = 0

    def m(self) -> int:
        return 1


class B:
    def __init__(self) -> None:
        self.n = 0

    def m(self) -> int:
        return 2


class C(A, B):
    def __init__(self) -> None:
        self.n = 0


#@ ensures \result == -1
def probe() -> int:
    c = C()
    return c.m()
