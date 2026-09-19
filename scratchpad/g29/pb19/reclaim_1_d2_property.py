_ = 0  # anchor


class C:
    def __init__(self) -> None:
        self.n = 2

    @property
    def area(self) -> int:
        return self.n * 10


#@ ensures \result == 1
def probe() -> int:
    c = C()
    return c.area
