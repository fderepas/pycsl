r"""G29 U3 — #150 composition: the base default is a MODULE CONSTANT (unknown)."""
_ = 0  # anchor
K = 5


class A:
    def __init__(self, k: int = K) -> None:
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
