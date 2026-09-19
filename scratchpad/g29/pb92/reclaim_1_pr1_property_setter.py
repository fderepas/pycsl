_ = 0  # anchor


class C:
    def __init__(self) -> None:
        self._n = 1

    @property
    def n(self) -> int:
        return self._n

    @n.setter
    def n(self, v: int) -> None:
        self._n = v * 10


#@ ensures \result == 1
def probe() -> int:
    c = C()
    c.n = 5
    return c.n
