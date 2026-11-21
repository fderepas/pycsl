_ = 0  # anchor


class C:
    def __init__(self) -> None:
        self.n = 0

    @staticmethod
    def k() -> int:
        return 4


#@ ensures \result == -1
def probe() -> int:
    return C.k()
