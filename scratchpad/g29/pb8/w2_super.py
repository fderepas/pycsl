_ = 0  # anchor


class A:
    def __init__(self) -> None:
        self.n = 1

    def val(self) -> int:
        return self.n


class B(A):
    def __init__(self) -> None:
        super().__init__()
        self.n = 5

    #@ ensures \result == 1
    def val(self) -> int:
        return super().val()


def probe() -> int:
    return B().val()
