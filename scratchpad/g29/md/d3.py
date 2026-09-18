r"""G29 MD3 — property setter clamps."""
_ = 0  # anchor


class C:
    def __init__(self) -> None:
        self._v = 0

    @property
    def v(self) -> int:
        return self._v

    @v.setter
    def v(self, val: int) -> None:
        self._v = 0 if val < 0 else val


#@ ensures \result == -5
def probe() -> int:
    c = C()
    c.v = -5
    return c.v


if __name__ == "__main__":
    print("CPython:", probe())
