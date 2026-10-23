r"""G29 P10 — route #150 draft: the subclass OVERWRITES the base field after `super().__init__`."""
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
        self.x = 3


#@ ensures \result == 3
#@ assigns \nothing
def probe() -> int:
    b = B(7)
    return b.get()


if __name__ == "__main__":
    print("CPython:", probe())
