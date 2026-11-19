r"""G29 GL-H2 — inlined method local shares a name with a caller local."""
_ = 0  # anchor


class C:
    def __init__(self, x: int) -> None:
        self.x = x

    def f(self, d: int) -> int:
        t = d * 10
        return t


_g = C(0)


#@ ensures \result == 10
def probe() -> int:
    t = 1
    _g.f(5)
    return t * 10


if __name__ == "__main__":
    print("CPython:", probe())
