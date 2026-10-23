r"""G29 P9 — route #150 draft: a base whose OWN constructor starts with `super().__init__()` (object)."""
_ = 0  # anchor


class A:
    def __init__(self, k: int) -> None:
        super().__init__()
        self.x = k

    #@ requires True
    #@ ensures \result == self.x
    def get(self) -> int:
        return self.x


class B(A):
    def __init__(self, k: int) -> None:
        super().__init__(k + 100)


#@ ensures \result == 107
#@ assigns \nothing
def probe() -> int:
    b = B(7)
    return b.get()


if __name__ == "__main__":
    print("CPython:", probe())
