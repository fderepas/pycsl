_ = 0  # anchor


class A:
    def __init__(self) -> None:
        self.n = 0

    #@ ensures \result == 99
    def m(self) -> int:
        return 1


class B(A):
    def m(self) -> int:
        return 2


#@ ensures \result == 99
def probe() -> int:
    b = B()
    return b.m()
