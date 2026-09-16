r"""G29 U5 — #150 composition x #153: the subclass REBINDS its parameter before `super().__init__(k)`."""
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
        super().__init__(k)
        k = 3


#@ ensures \result == 9
#@ assigns \nothing
def probe() -> int:
    b = B(9)
    return b.get()


if __name__ == "__main__":
    print("CPython:", probe())
