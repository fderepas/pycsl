_ = 0  # anchor


class A:
    def __init__(self) -> None:
        self.n = 0

    #@ ensures \result == 1
    def val(self) -> int:
        return 1


class B(A):
    def val(self) -> int:
        return 2


def use(a: A) -> int:
    return a.val()


#@ ensures \result == 1
def probe() -> int:
    b = B()
    return use(b)
