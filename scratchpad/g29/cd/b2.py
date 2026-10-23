r"""G29 CD2 — a property computes from a field."""
_ = 0  # anchor


class A:
    def __init__(self, x: int) -> None:
        self.x = x

    @property
    def double(self) -> int:
        return self.x * 2


#@ ensures \result == 3
def probe() -> int:
    a = A(3)
    return a.double


if __name__ == "__main__":
    print("CPython:", probe())
