# u78 helper for witness 10542 (review rt88 K1, route #634): a pure `R.total` and a subclass `D(R)` whose override of `total` writes `self.a`.


class R:
    def __init__(self, a: int = 0) -> None:
        self.a = a

    #@ ensures \result == self.a
    def total(self) -> int:
        return self.a


class D(R):
    def __init__(self, a: int = 0) -> None:
        self.a = a

    #@ ensures \result == 0
    def total(self) -> int:
        self.a = 5
        return 0
