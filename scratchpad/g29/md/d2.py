r"""G29 MD2 — classmethod factory."""
_ = 0  # anchor


class C:
    def __init__(self, x: int) -> None:
        self.x = x

    @classmethod
    def make(cls) -> "C":
        return cls(7)


#@ ensures \result == 0
def probe() -> int:
    c = C.make()
    return c.x


if __name__ == "__main__":
    print("CPython:", probe())
