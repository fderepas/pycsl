_ = 0  # anchor


class C:
    def __init__(self) -> None:
        self.n = 3


#@ ensures \result == 3
def probe() -> int:
    c = C()
    c.n += 4
    return c.n
