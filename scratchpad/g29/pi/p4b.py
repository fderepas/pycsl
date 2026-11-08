r"""G29 P4B — `super().__init__(k + 100)`, the base field read through an INHERITED method."""
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


#@ ensures \result == 0
#@ assigns \nothing
def probe() -> int:
    b = B(7)
    return b.get()


if __name__ == "__main__":
    print("CPython:", probe())
