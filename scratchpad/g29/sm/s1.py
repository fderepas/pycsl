r"""G29 SM1 — `super().m()` inside an overriding method."""
_ = 0  # anchor


class A:
    def __init__(self) -> None:
        self.n = 1

    #@ ensures \result == 1
    def m(self) -> int:
        return 1


class B(A):
    #@ ensures \result == 5
    def m(self) -> int:
        return super().m() + 1


if __name__ == "__main__":
    print("CPython:", B().m())
