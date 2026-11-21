r"""G29 U6 — the rebinding happens INSIDE the super call argument via a walrus."""
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
        super().__init__((k := k + 1))


#@ ensures \result == 9
#@ assigns \nothing
def probe() -> int:
    b = B(9)
    return b.get()


if __name__ == "__main__":
    print("CPython:", probe())
