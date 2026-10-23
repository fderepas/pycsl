_ = 0  # anchor


class C:
    def __init__(self) -> None:
        self.n = 0

    @classmethod
    def make(cls) -> int:
        return 7


#@ ensures \result == 0
def probe() -> int:
    return C.make()
