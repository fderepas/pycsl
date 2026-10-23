r"""G29 U4 — two-level composition: `C` -> `B.__init__(): super().__init__(7)` -> `A.__init__(k)`."""
_ = 0  # anchor


class A:
    def __init__(self, k: int) -> None:
        self.x = k

    #@ requires True
    #@ ensures \result == self.x
    def get(self) -> int:
        return self.x


class B(A):
    def __init__(self) -> None:
        super().__init__(7)


class C(B):
    def __init__(self) -> None:
        super().__init__()


#@ ensures \result == 0
#@ assigns \nothing
def probe() -> int:
    c = C()
    return c.get()


if __name__ == "__main__":
    print("CPython:", probe())
