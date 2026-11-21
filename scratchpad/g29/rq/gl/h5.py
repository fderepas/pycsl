r"""G29 GL-H5 — inlined method param named like the receiver global."""
_ = 0  # anchor


class C:
    def __init__(self, x: int) -> None:
        self.x = x

    def f(self, x: int) -> int:
        return self.x + x


_g = C(0)


#@ ensures \result == 10
def probe() -> int:
    return _g.f(5)


if __name__ == "__main__":
    print("CPython:", probe())
