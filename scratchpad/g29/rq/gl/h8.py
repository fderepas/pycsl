r"""G29 GL-H8 — the caller shadows the global K, and the inlined method reads K."""
_ = 0  # anchor
K = 3


class C:
    def __init__(self, x: int) -> None:
        self.x = x

    def f(self) -> int:
        return K


_g = C(0)


#@ ensures \result == 3
def probe() -> int:
    K = 9
    return _g.f() + K - 9


if __name__ == "__main__":
    print("CPython:", probe())
