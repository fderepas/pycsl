r"""G29 SM2 — a base method calling `self.m()` dispatches to the OVERRIDE (CPython 7)."""
_ = 0  # anchor


class A:
    def __init__(self) -> None:
        self.n = 1

    #@ ensures \result == 1
    def m(self) -> int:
        return 1

    #@ ensures \result == 1
    def call_m(self) -> int:
        return self.m()


class B(A):
    #@ ensures \result == 7
    def m(self) -> int:
        return 7


#@ ensures \result == 1
def probe() -> int:
    b = B()
    return b.call_m()


if __name__ == "__main__":
    print("CPython:", probe())
