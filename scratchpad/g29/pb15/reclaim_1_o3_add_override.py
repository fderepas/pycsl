_ = 0  # anchor


class C:
    def __init__(self) -> None:
        self.n = 1

    def __add__(self, other: int) -> int:
        return 100


#@ ensures \result == 1
def probe() -> int:
    a = C()
    return a + 1
