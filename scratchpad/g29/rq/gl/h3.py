r"""G29 GL-H3 — inlined method reads a module global name that the caller shadows with a local."""
_ = 0  # anchor
K = 3


class C:
    def __init__(self, x: int) -> None:
        self.x = x

    def f(self) -> int:
        return K


_g = C(0)


#@ ensures \result == 9
def probe() -> int:
    K = 9
    return _g.f()


if __name__ == "__main__":
    print("CPython:", probe())
