r"""G29 GL-H6 — inlined method binds a tuple target named like a caller local."""
_ = 0  # anchor


class C:
    def __init__(self, x: int) -> None:
        self.x = x

    def f(self, d: int) -> int:
        a, b = d, d
        return a + b


_g = C(0)


#@ ensures \result == 100
def probe() -> int:
    a = 7
    _g.f(100)
    return a


if __name__ == "__main__":
    print("CPython:", probe())
