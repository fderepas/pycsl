r"""G29 Q2 — a PROPERTY SETTER intercepts the constructor's `self.x = k`."""
_ = 0  # anchor


class P:
    def __init__(self, k: int) -> None:
        self._x = 0
        self.x = k

    @property
    def x(self) -> int:
        return self._x

    @x.setter
    def x(self, v: int) -> None:
        self._x = v * 2


#@ ensures \result == 0
#@ assigns \nothing
def probe() -> int:
    p = P(5)
    return p._x


if __name__ == "__main__":
    print("CPython:", probe())
