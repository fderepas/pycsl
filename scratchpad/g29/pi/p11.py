r"""G29 P11 — route #150 draft: `super().__init__` argument over a MODULE CONSTANT (not a param)."""
_ = 0  # anchor
K = 50


class A:
    def __init__(self, k: int) -> None:
        self.x = k

    #@ requires True
    #@ ensures \result == self.x
    def get(self) -> int:
        return self.x


class B(A):
    def __init__(self) -> None:
        super().__init__(K)


#@ ensures \result == 0
#@ assigns \nothing
def probe() -> int:
    b = B()
    return b.get()


if __name__ == "__main__":
    print("CPython:", probe())
