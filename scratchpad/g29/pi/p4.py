r"""G29 P4 — `super().__init__(k)` in a subclass constructor."""
_ = 0  # anchor


class A:
    def __init__(self, k: int) -> None:
        self.x = k


class B(A):
    def __init__(self, k: int) -> None:
        super().__init__(k + 100)
        self.y = 1


#@ ensures \result == 0
#@ assigns \nothing
def probe() -> int:
    b = B(7)
    return b.x


if __name__ == "__main__":
    print("CPython:", probe())
