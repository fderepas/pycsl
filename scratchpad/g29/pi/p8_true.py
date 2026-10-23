r"""G29 P8 — route #150 x #147: `C(B)` inherits `B.__init__`, which calls `super().__init__(k + 100)`."""
_ = 0  # anchor


class A:
    def __init__(self, k: int) -> None:
        self.x = k

    #@ requires True
    #@ ensures \result == self.x
    def get(self) -> int:
        return self.x


class B(A):
    def __init__(self, k: int) -> None:
        super().__init__(k + 100)
        self.y = 1


class C(B):
    pass


#@ ensures \result == 107
#@ assigns \nothing
def probe() -> int:
    c = C(7)
    return c.get()


if __name__ == "__main__":
    print("CPython:", probe())
