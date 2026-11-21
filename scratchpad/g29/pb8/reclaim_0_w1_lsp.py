_ = 0  # anchor


class A:
    def __init__(self) -> None:
        self.n = 0

    #@ ensures \result == 0
    def val(self) -> int:
        return 1


class B(A):
    def val(self) -> int:
        return 2


#@ ensures \result == 0
def probe() -> int:
    b: A = B()
    return b.val()
