r"""G29 U2 — #150 composition x #82: the base's KEYWORD-ONLY defaulted parameter."""
_ = 0  # anchor


class A:
    def __init__(self, *, k: int = 5) -> None:
        self.x = k

    #@ requires True
    #@ ensures \result == self.x
    def get(self) -> int:
        return self.x


class B(A):
    def __init__(self) -> None:
        super().__init__()


#@ ensures \result == 5
#@ assigns \nothing
def probe() -> int:
    b = B()
    return b.get()


if __name__ == "__main__":
    print("CPython:", probe())
