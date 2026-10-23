r"""G29 CD4 — __eq__ override always True."""
_ = 0  # anchor


class A:
    def __init__(self, x: int) -> None:
        self.x = x

    def __eq__(self, other: object) -> bool:
        return True


#@ ensures \result == False
def probe() -> bool:
    return A(1) == A(2)


if __name__ == "__main__":
    print("CPython:", probe())
