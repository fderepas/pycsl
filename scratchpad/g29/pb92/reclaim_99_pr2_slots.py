_ = 0  # anchor


class C:
    __slots__ = ("n",)

    def __init__(self) -> None:
        self.n = 1


#@ ensures \result == 99
def probe() -> int:
    c = C()
    return c.n
