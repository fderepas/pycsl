r"""G29 GL-H1 — inlined method rebinds its formal; the actual is a caller Var."""
_ = 0  # anchor


class C:
    def __init__(self, x: int) -> None:
        self.x = x

    def f(self, d: int) -> int:
        d = d + 1
        return d


_g = C(0)


#@ ensures \result == 2
def probe() -> int:
    k = 1
    _g.f(k)
    return k


if __name__ == "__main__":
    print("CPython:", probe())
