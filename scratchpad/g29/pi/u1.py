r"""G29 U1 — #150 composition x #149: `super().__init__()` omits the base's DEFAULTED parameter."""
_ = 0  # anchor


class A:
    def __init__(self, k: int = 5) -> None:
        self.x = k

    #@ requires True
    #@ ensures \result == self.x
    def get(self) -> int:
        return self.x


class B(A):
    def __init__(self) -> None:
        super().__init__()


#@ ensures \result == 0
#@ assigns \nothing
def probe() -> int:
    b = B()
    return b.get()


if __name__ == "__main__":
    print("CPython:", probe())
